from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from fastapi import Request
from langchain_core.prompts import PromptTemplate
from llm.llm_factory import LLMFactory
from enums import LLMProvider
from models import get_db
from utils.logger import logger

router = APIRouter(prefix="/api/conversation", tags=["Conversation"])


@router.post("/send-message")
async def send_message(body: Request, db: Session = Depends(get_db)):
    try:
        body = await body.json()
        prompt_text = body.get("prompt")

        llm = LLMFactory.create(
            LLMProvider.Deepseek,
            model="deepseek-v3.1",
            api_key="sk-72b635b190514c8b90cfcbfe750fa61a",
        )

        prompt = PromptTemplate.from_template("{prompt_text}")
        chain = prompt | llm

        def stream_generator():
            try:
                for chunk in chain.stream({"prompt_text": prompt_text}):
                    yield chunk
            except Exception as e:
                logger.exception("stream error")
                yield f"\n[Error] {str(e)}\n"

        return StreamingResponse(
            stream_generator(), media_type="text/plain; charset=utf-8"
        )
    except Exception as e:
        logger.error(e)
