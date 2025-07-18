from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from .base import BaseModel


class Model(BaseModel):
    __tablename__ = "model"

    name = Column(String, nullable=False, unique=True, default="")
    display_name = Column(String, nullable=True, default="")
    types = Column(ARRAY(String), nullable=True)  # 模型类型
    model_provider_id = Column(
        Integer, ForeignKey("model_provider.id"), nullable=False
    )  # 模型提供商ID
    max_context_tokens = Column(String, nullable=True)
    token_limit = Column(Integer, nullable=True)  # 令牌限制

    # 开启双向绑定
    provider = relationship("ModelProvider", back_populates="models")
