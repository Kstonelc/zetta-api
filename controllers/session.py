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


@router.post("/send-message")
async def send_message(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        prompt_text = body.get("prompt")
        model_name = body.get("modelName")
        modelProvider = body.get("modelProvider")

        llm = LLMFactory.create(
            modelProvider,
            model=model_name,
            api_key="sk-72b635b190514c8b90cfcbfe750fa61a",
            stop=["\n", "\n\n"],
        )

        prompt = PromptTemplate.from_template("{prompt_text}")
        chain = prompt | llm

        async def stream_generator():
            try:
                async for chunk in chain.astream({"prompt_text": prompt_text}):
                    if await request.is_disconnected():
                        break
                    yield chunk
                    await asyncio.sleep(0)
            except (ClientDisconnect, asyncio.CancelledError):
                pass
            except Exception as e:
                logger.exception("stream error")
                yield f"\n[Error] {e}\n"

        return StreamingResponse(
            stream_generator(), media_type="text/plain; charset=utf-8"
        )
    except Exception as e:
        logger.error(e)
