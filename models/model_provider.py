from sqlalchemy import (
    Column,
    String,
    Text,
)
from .base import BaseModel
from sqlalchemy.orm import relationship


class ModelProvider(BaseModel):
    __tablename__ = "model_provider"

    name = Column(String, nullable=False, unique=True)
    api_key = Column(String, nullable=True)  # API KEY
    desc = Column(Text, nullable=True)

    models = relationship("Model", back_populates="provider")

    tenants = relationship(
        "Tenant",
        secondary="model_provider_tenant_join",
        back_populates="model_providers",
        overlaps="tenant_model_provider_joins",
    )
    tenant_model_provider_joins = relationship(
        "ModelProviderTenantJoin",
        back_populates="model_provider",
        cascade="all, delete-orphan",
        overlaps="tenants,model_providers",
    )
