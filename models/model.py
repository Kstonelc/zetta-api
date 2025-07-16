from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class Model(BaseModel):
    __tablename__ = "model"

    id = Column(Integer, primary_key=True, index=True)
    active = Column(Boolean, default=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    display_name = Column(String, nullable=True)
    provider_id = Column(
        Integer, ForeignKey("model_provider.id"), nullable=False
    )  # 模型提供商ID
    api_key = Column(String, nullable=True)  # API KEY
    max_context_tokens = Column(Integer, nullable=True)
    token_limit = Column(Integer, nullable=True)  # 令牌限制

    # 开启双向绑定
    provider = relationship("ModelProvider", back_populates="model")
