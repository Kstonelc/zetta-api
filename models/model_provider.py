from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class ModelProvider(BaseModel):
    __tablename__ = "model_provider"

    name = Column(String, nullable=False, unique=True)
    api_key = Column(String, nullable=True)  # API KEY
    desc = Column(Text)

    # 双向绑定 级联删除
    models = relationship(
        "Model", back_populates="provider", cascade="all, delete-orphan"
    )
