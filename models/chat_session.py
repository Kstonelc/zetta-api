from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    create_engine,
)
from .base import BaseModel
from sqlalchemy.orm import relationship
import datetime


class ChatSession(BaseModel):
    __tablename__ = "chat_session"

    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)  # 当前回话总结标题(AI生成)

    # 删除session 级联删除message
    chat_messages = relationship(
        "ChatMessage", back_populates="chat_session", cascade="all, delete-orphan"
    )


class ChatMessage(BaseModel):
    __tablename__ = "chat_message"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_session.id"), nullable=False)
    sender = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    session = relationship("ChatSession", back_populates="chat_message")
