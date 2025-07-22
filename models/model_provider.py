from sqlalchemy import Column, String, Text
from .base import BaseModel
from sqlalchemy.orm import relationship
from .model import Model


class ModelProvider(BaseModel):
    __tablename__ = "model_provider"

    name = Column(String, nullable=False, unique=True)
    api_key = Column(String, nullable=True)  # API KEY
    desc = Column(Text)

    models = relationship("Model", back_populates="provider", passive_deletes=True)
