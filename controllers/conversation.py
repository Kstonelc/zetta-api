from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from sqlalchemy import and_, desc, func, select
from fastapi import Request
from langchain_core.prompts import PromptTemplate
from sqlalchemy.testing.suite.test_reflection import users

from llm.llm_factory import LLMFactory
from llm.web_search import web_search
import asyncio
import json
import time
from enums import LLMProvider, ConversationStatus, SenderType
from models.conversation import Message
from models import get_db, Conversation
from langchain_core.messages import HumanMessage, SystemMessage
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
from utils.common import get_domain

router = APIRouter(prefix="/api/conversation", tags=["conversation"])


def json_line(obj: dict) -> bytes:
    # NDJSON 每个JSON 结尾加换行
    return (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")


@router.post("/chat")
async def chat(
    request: Request,
    body: ConversationChatRequest,
    db: Session = Depends(get_db),
    token=Depends(verify_token),
):

    def update_conversation_message(db, assistant_message_id, answer_buf, thinking_buf):
        db.query(Message).filter(Message.id == assistant_message_id).update(
            {"content": answer_buf, "thinking": thinking_buf}
        )
        db.commit()

    try:
        prompt_text = body.promptText
        model_name = body.modelName
        modelProvider = body.modelProvider
        assistant_message_id = body.assistantMessageId
        is_deep_think = body.isDeepThink
        is_online = body.isOnline

        llm = LLMFactory.create(
            modelProvider,
            model=model_name,
            api_key="sk-72b635b190514c8b90cfcbfe750fa61a",
            enable_deep_think=is_deep_think,
        )

        async def stream_generator():
            answer_buf = ""
            thinking_buf = ""

            try:
                if await request.is_disconnected():
                    logger.error("Client disconnected")
                    return

                # 构建消息列表
                system_prompt = """你是一个有帮助的AI助手。请根据以下指导原则回答：
                    1. 如果提供了搜索信息，请基于这些信息生成准确、客观的回答
                    2. 如果信息复杂，请先总结再详细说明
                    3. 保持回答专业且易于理解"""
                prompts = []
                prompts.append(SystemMessage(content=system_prompt))
                prompts.append(HumanMessage(content=prompt_text))

                # yield json_line(
                #     {
                #         "type": "retrieve_start",
                #         "delta": "正在检索",
                #         "section": "retrieve_start",
                #     }
                # )

                # time.sleep(4)

                # yield json_line(
                #     {
                #         "type": "retrieve_end",
                #         "delta": "检索完成",
                #         "section": "retrieve_end",
                #     }
                # )

                for chunk in llm.stream(prompts):
                    if hasattr(chunk, "content"):
                        ak = getattr(chunk, "additional_kwargs", None) or {}
                        phase = ak.get("phase")  # thinking" or "answer" or None
                        reasoning_delta = ak.get("reasoning_content")

                        if phase == "thinking" or reasoning_delta is not None:
                            delta = (
                                reasoning_delta
                                if reasoning_delta is not None
                                else (chunk.content or "")
                            )
                            if delta:
                                thinking_buf += delta
                                yield json_line({"type": "thinking", "delta": delta})
                        else:
                            delta = chunk.content or ""
                            if delta:
                                answer_buf += delta
                                yield json_line({"type": "answer", "delta": delta})
                    else:
                        # 退化为 str：按答案处理
                        text_delta = str(chunk)
                        if text_delta:
                            answer_buf += text_delta
                            yield json_line({"type": "answer", "delta": text_delta})

                # 正常结束
                yield json_line(
                    {
                        "type": "done",
                        "answerLength": len(answer_buf),
                        "thinkingLength": len(thinking_buf),
                    }
                )
            except (asyncio.CancelledError, GeneratorExit):
                logger.warning("Stream_generator cancelled due to client disconnect")
                raise
            except Exception as e:
                if not await request.is_disconnected():
                    yield f"\n[Stream Error] {str(e)}\n"
            finally:
                # 流结束时触发的操作
                logger.info(f"Stream ended. Final text length: {len(answer_buf)}")

                # 更新数据库
                update_conversation_message(
                    db, assistant_message_id, answer_buf, thinking_buf
                )

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
