from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from fastapi import Request
from llm.qwen import QWProvider
from llm.deepseek import DeepseekProvider
from models import get_db
from enums import QWModelType
from utils.logger import logger

router = APIRouter(prefix="/api/conversation", tags=["Conversation"])


@router.post("/send-message")
async def send_message(body: Request, db: Session = Depends(get_db)):
    try:
        body = await body.json()  # ✅ 需要加 await
        prompt = body.get("prompt")
        # llm = QWProvider(model_name=QWModelType.qw_turbo)
        llm = DeepseekProvider(
            api_key="sk-a59c3aba2d6347b8855e29373cf0ff69", model="deepseek-chat"
        )

        def stream_generator():
            try:
                for chunk in llm.stream(prompt):
                    yield chunk  # 持续输出响应内容
            except Exception as e:
                yield f"\n[Error] {str(e)}\n"

        return StreamingResponse(stream_generator(), media_type="text/plain")
    except Exception as e:
        logger.error(e)
