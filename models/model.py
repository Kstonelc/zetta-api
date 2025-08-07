from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Model(BaseModel):
    __tablename__ = "model"

    name = Column(String(255), nullable=False, unique=True, default="")
    display_name = Column(String(255), nullable=True, default="")
    types = Column(ARRAY(String(255)), nullable=True)  # 模型类型
    model_provider_id = Column(
        UUID, ForeignKey("model_provider.id"), nullable=True
    )  # 模型提供商ID
    max_context_tokens = Column(String(255), nullable=True)
    token_limit = Column(Integer, nullable=True)  # 令牌限制

    provider = relationship("ModelProvider", back_populates="models")
