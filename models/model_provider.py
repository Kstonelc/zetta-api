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

    model_provider_tenant_joins = relationship(
        "ModelProviderTenantJoin",
        back_populates="model_provider",
        passive_deletes=True,
    )

    tenants = relationship(
        "Tenant",
        secondary="model_provider_tenant_join",
        viewonly=True,
        back_populates="model_providers",
        overlaps="model_provider_tenant_joins, model_providers",
    )
