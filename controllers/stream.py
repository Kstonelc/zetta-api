from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Optional
import asyncio
import json
from redis import Redis
from config import settings


router = APIRouter(prefix="/api/stream", tags=["stream"])


def _r() -> Redis:
    return Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


async def _sse_event(
    data: str, event: Optional[str] = None, eid: Optional[str] = None
) -> bytes:
    parts = []
    if event:
        parts.append(f"event: {event}\n")
    if eid:
        parts.append(f"id: {eid}\n")
    for line in data.splitlines() or [""]:
        parts.append(f"data: {line}\n")
    parts.append("\n")
    return "".join(parts).encode("utf-8")


@router.get("/jobs/{job_id}")
async def stream_job(job_id: str, request: Request, since: int = 0):
    async def event_generator() -> AsyncGenerator[bytes, None]:
        r = _r()
        pubsub = r.pubsub()
        channel = f"chat_stream_task:job:{job_id}"
        pubsub.subscribe(channel)

        try:
            # 1) 先补发历史增量（列表索引与 offset 对齐：index=offset-1）
            start_index = max(since, 0)
            if start_index > 0:
                start_index = (
                    start_index  # offset=N -> 从列表 index=N 开始（之前已消费 N 条）
                )
            chunks = r.lrange(f"job:{job_id}:chunks", start_index, -1)
            for raw in chunks:
                try:
                    item = json.loads(raw)
                    data = item.get("text", "")
                    offset = item.get("offset")
                    yield await _sse_event(data, event="token", eid=str(offset))
                except Exception:
                    # 跳过坏数据
                    continue

            # 2) 实时订阅并转发
            last_heartbeat = 0.0
            while True:
                if await request.is_disconnected():
                    break

                message = pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1.0
                )
                if message and message.get("type") == "message":
                    try:
                        payload = json.loads(message.get("data", b"{}"))
                    except Exception:
                        payload = {"type": "token", "data": ""}

                    mtype = payload.get("type")
                    if mtype == "token":
                        data = payload.get("data", "")
                        offset = payload.get("offset")
                        yield await _sse_event(
                            data,
                            event="token",
                            eid=str(offset) if offset is not None else None,
                        )
                    elif mtype == "done":
                        yield await _sse_event("", event="done")
                        break
                    elif mtype == "error":
                        err = payload.get("message", "error")
                        yield await _sse_event(err, event="error")
                        break

                # 心跳，保持连接活跃
                now = asyncio.get_event_loop().time()
                if now - last_heartbeat > 15:
                    last_heartbeat = now
                    yield b": ping\n\n"
        finally:
            try:
                pubsub.unsubscribe(channel)
            except Exception:
                pass
            try:
                pubsub.close()
            except Exception:
                pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")
