from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from fastapi import Request
from langchain_core.prompts import PromptTemplate
from llm.llm_factory import LLMFactory
import asyncio
from starlette.requests import ClientDisconnect
from enums import LLMProvider
from models import get_db
from utils.logger import logger

router = APIRouter(prefix="/api/session", tags=["session"])


@router.post("/chat")
async def send_message(request: Request, db: Session = Depends(get_db)):
    response = {}
    try:
        body = await request.json()
        prompt_text = body.get("prompt")
        model_name = body.get("modelName")
        modelProvider = body.get("modelProvider")

        llm = LLMFactory.create(
            modelProvider,
            model=model_name,
            api_key="sk-72b635b190514c8b90cfcbfe750fa61a",
        )

        prompt = PromptTemplate.from_template("{prompt_text}")
        chain = prompt | llm

        async def stream_generator():
            try:
                if await request.is_disconnected():
                    logger.error("Client disconnected")
                    return

                async for chunk in chain.astream({"prompt_text": prompt_text}):
                    if await request.is_disconnected():
                        logger.error("Client disconnected")
                        break
                    text = None
                    # LangChain 常见分支
                    if hasattr(chunk, "content"):  # AIMessageChunk / BaseMessageChunk
                        text = chunk.content
                    elif hasattr(chunk, "delta"):  # 一些模型的 token 增量字段
                        text = chunk.delta
                    elif isinstance(chunk, str):
                        text = chunk
                    else:
                        # 兜底：不要把对象 repr 输出到前端
                        text = ""

                    if text:
                        # 统一成 bytes，避免编码问题
                        yield text.encode("utf-8")

            except (asyncio.CancelledError, GeneratorExit):
                logger.warning("Stream_generator cancelled due to client disconnect")
                raise
            except Exception as e:
                if not await request.is_disconnected():
                    yield f"\n[Stream Error] {str(e)}\n"

        return StreamingResponse(
            stream_generator(), media_type="text/plain; charset=utf-8"
        )
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "send message failed"}
        return response
