from sqlalchemy import (
    Column,
    String,
    Text,
)
from .base import BaseModel
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship


class ModelProvider(BaseModel):
    __tablename__ = "model_provider"

    name = Column(String, nullable=False, unique=True)
    api_key = Column(String, nullable=True)  # API KEY
    desc = Column(Text, nullable=True)

    models = relationship("Model", back_populates="provider")

    tenant_links = relationship(
        "ModelProviderTenantJoin", back_populates="model_provider"
    )
    tenants = association_proxy("tenant_links", "tenant")
