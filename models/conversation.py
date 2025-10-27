from sqlalchemy import (
    Column,
    Integer,
    String,
    BigInteger,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    create_engine,
)
from .base import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from enums import SenderType
from sqlalchemy.orm import relationship
import datetime


class Conversation(BaseModel):
    __tablename__ = "conversation"

    tenant_id = Column(UUID, nullable=False)
    user_id = Column(UUID, nullable=False)
    name = Column(String, nullable=True)  # 当前回话总结标题(AI生成)
    model_id = Column(UUID, nullable=False)

    # 删除session 级联删除message
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(BaseModel):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id"), nullable=False)
    sequence = Column(BigInteger, nullable=False)  # 序列
    role = Column(SenderType, nullable=False)  # 发送者类型
    tokens = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
