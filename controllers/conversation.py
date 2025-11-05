from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from sqlalchemy import and_, desc, func, select
from fastapi import Request
from langchain_core.prompts import PromptTemplate
from sqlalchemy.testing.suite.test_reflection import users

from llm.llm_factory import LLMFactory
import asyncio
from enums import LLMProvider, ConversationStatus, SenderType
from models.conversation import Message
from models import get_db, Conversation
from schemas.conversation import (
    ConversationChatRequest,
    ConversationCreateRequest,
    ConversationQueryRequest,
    ConversationMessageQueryRequest,
    ConversationMessageCreateRequest,
    ConversationMessageUpdateRequest,
)
from fastapi import BackgroundTasks
from utils.jwt import verify_token
from utils.logger import logger

router = APIRouter(prefix="/api/conversation", tags=["conversation"])


@router.post("/chat")
async def chat(
    request: Request,
    body: ConversationChatRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):

    def update_conversation_message(db, assistant_message_id, final_text):
        db.query(Message).filter(Message.id == assistant_message_id).update(
            {
                "content": final_text,
            }
        )
        db.commit()

    try:
        prompt_text = body.promptText
        model_name = body.modelName
        modelProvider = body.modelProvider
        assistant_message_id = body.assistantMessageId

        llm = LLMFactory.create(
            modelProvider,
            model="deepseek-r1",
            api_key="sk-72b635b190514c8b90cfcbfe750fa61a",
            enable_deep_think=True,
        )

        prompt = PromptTemplate.from_template("{prompt_text}")
        chain = prompt | llm

        async def stream_generator():
            final_text = ""
            try:
                if await request.is_disconnected():
                    logger.error("Client disconnected")
                    return

                async for chunk in chain.astream({"prompt_text": prompt_text}):
                    if await request.is_disconnected():
                        logger.error("Client disconnected")
                        break
                    text = None
                    print(111, chunk)
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
                        final_text += text
                        # 统一成 bytes，避免编码问题
                        yield text.encode("utf-8")

            except (asyncio.CancelledError, GeneratorExit):
                logger.warning("Stream_generator cancelled due to client disconnect")
                raise
            except Exception as e:
                if not await request.is_disconnected():
                    yield f"\n[Stream Error] {str(e)}\n"
            finally:
                # 流结束时触发的操作
                logger.info(f"Stream ended. Final text length: {len(final_text)}")

                # 更新数据库
                if final_text and assistant_message_id:
                    try:
                        update_conversation_message(
                            db, assistant_message_id, final_text
                        )
                        logger.info(
                            f"Message {assistant_message_id} updated successfully"
                        )
                    except Exception as e:
                        logger.error(f"Failed to update message: {e}")

        return StreamingResponse(
            stream_generator(), media_type="text/plain; charset=utf-8"
        )
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "send message failed"}
        return response


@router.post("/create-conversation")
async def create_conversation(
    body: ConversationCreateRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        tenant_id = body.tenantId
        user_id = body.userId

        tmp_conversation = (
            db.query(Conversation)
            .filter(
                and_(
                    Conversation.tenant_id == tenant_id,
                    Conversation.user_id == user_id,
                    Conversation.status == ConversationStatus.Temporary.value,
                )
            )
            .first()
        )
        if tmp_conversation:
            response = {"ok": True, "data": {"conversation_id": tmp_conversation.id}}
            return
        new_conversation = Conversation(
            tenant_id=tenant_id,
            user_id=user_id,
            status=ConversationStatus.Temporary.value,
            name="新的对话",
        )
        db.add(new_conversation)
        db.commit()
        response = {"ok": True, "data": {"conversation_id": new_conversation.id}}
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "create conversation failed"}
    finally:
        return response


@router.post("/find-conversations")
async def find_conversations(
    body: ConversationQueryRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        tenant_id = body.tenantId
        user_id = body.userId
        conversation_status = body.conversationStatus

        filters = [
            Conversation.active.is_(True),
            Conversation.status.in_(conversation_status),
        ]
        if tenant_id is not None:
            filters.append(Conversation.tenant_id == tenant_id)
        if user_id is not None:
            filters.append(Conversation.user_id == user_id)

        conversations = (
            db.query(Conversation)
            .filter(and_(*filters))
            .order_by(desc(Conversation.created_at))
            .all()
        )
        response = {"ok": True, "data": conversations}
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "query conversation failed"}
    finally:
        return response


@router.post("/find-conversation")
async def find_conversation(
    body: ConversationQueryRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        conversation_id = body.conversationId

        conversation = (
            db.query(Conversation).filter(Conversation.id == conversation_id).first()
        )
        response = {"ok": True, "data": conversation}
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "find conversation failed"}
    finally:
        return response


@router.post("/find-messages")
async def find_messages(
    body: ConversationMessageQueryRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        conversation_id = body.conversationId

        messages = (
            db.query(Message)
            .filter(
                and_(
                    Message.conversation_id == conversation_id,
                    Conversation.active.is_(True),
                )
            )
            .order_by(Message.sequence)
            .all()
        )

        response = {"ok": True, "data": messages}
    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "query messages failed"}
    finally:
        return response


@router.post("/create-message")
async def create_message(
    body: ConversationMessageCreateRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        conversation_id = body.conversationId
        user_content = body.userContent
        assistant_content = body.assistantContent

        # 锁定会话 防止发生并发冲突
        db.execute(
            select(Conversation.id)
            .where(Conversation.id == conversation_id)
            .with_for_update()
        )
        # 获取下一个序列号
        res = db.execute(
            select(func.coalesce(func.max(Message.sequence) + 1, 1)).where(
                Message.conversation_id == conversation_id
            )
        )
        current_seq = res.scalar_one()
        user_seq = current_seq
        assistant_seq = current_seq + 1
        m_user = Message(
            conversation_id=conversation_id,
            sequence=user_seq,
            role=SenderType.User.value,
            content=user_content,
        )
        m_assistant = Message(
            conversation_id=conversation_id,
            sequence=assistant_seq,
            role=SenderType.Assistant.value,
            content=assistant_content,
        )

        db.add_all([m_user, m_assistant])
        db.commit()
        # TODO 极端并发处理？？
        db.refresh(m_user)
        db.refresh(m_assistant)

        # 更新对应的 conversation 为 Active
        db.query(Conversation).filter(Conversation.id == conversation_id).update(
            {"status": ConversationStatus.Active.value}, synchronize_session=False
        )
        db.commit()

        db.query(Conversation).filter(Conversation.id == conversation_id).update(
            {"name": user_content}, synchronize_session=False
        )
        db.commit()

        response = {
            "ok": True,
            "data": {
                "user_message_id": m_user.id,
                "assistant_message_id": m_assistant.id,
            },
        }

    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "create message failed"}
    finally:
        return response


@router.post("/update-message")
async def update_message(
    body: ConversationMessageUpdateRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):
    response = {}
    try:
        message_id = body.messageId
        assistant_content = body.assistantContent

        db.query(Message).filter(Message.id == message_id).update(
            {"content": assistant_content}
        )
        db.commit()

        response = {"ok": True, "data": "update message success"}

    except Exception as e:
        logger.error(e)
        response = {"ok": False, "message": "update message failed"}
    finally:
        return response
