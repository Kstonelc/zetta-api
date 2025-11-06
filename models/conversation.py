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
    UniqueConstraint,
    Index,
)
from .base import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from enums import SenderType, ConversationStatus
from sqlalchemy.orm import relationship


class Conversation(BaseModel):
    __tablename__ = "conversation"

    tenant_id = Column(UUID, nullable=False)
    user_id = Column(UUID, nullable=False)
    name = Column(String, nullable=True)  # 当前回话总结标题(AI生成)
    status = Column(
        Integer,
        default=ConversationStatus.Temporary.value,
        nullable=False,
    )
    model_id = Column(UUID, nullable=True)
    __table_args__ = (
        # 条件唯一索引：同一个 tenant + user 只能有一个 Temporary
        Index(
            "uq_conversation_tenant_user_temp",
            "tenant_id",
            "user_id",
            unique=True,
            postgresql_where=(status == ConversationStatus.Temporary.value),
        ),
    )

    # 删除session 级联删除message
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(BaseModel):
    __tablename__ = "message"
    __table_args__ = (
        UniqueConstraint("conversation_id", "sequence", name="uq_message_conv_seq"),
        Index("index_message_conv_seq", "conversation_id", "sequence"),
    )

    conversation_id = Column(UUID, ForeignKey("conversation.id"), nullable=False)
    sequence = Column(BigInteger, nullable=False)  # 序列
    role = Column(Integer, nullable=False)  # 发送者类型
    tokens = Column(Integer, nullable=True)  # 消耗的token
    thinking = Column(Text, nullable=True)  # 思考过程
    content = Column(Text, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
