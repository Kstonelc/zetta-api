from sqlalchemy import Column, Integer, String, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class ModelProvider(BaseModel):
    __tablename__ = "model_provider"

    id = Column(Integer, primary_key=True, index=True)
    active = Column(Boolean, default=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    desc = Column(Text)

    # 双向绑定 级联删除
    model = relationship(
        "Model", back_populates="provider", cascade="all, delete-orphan"
    )
