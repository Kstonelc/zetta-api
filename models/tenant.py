from sqlalchemy import (
    Column,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from .base import BaseModel


class Tenant(BaseModel):
    __tablename__ = "tenant"

    name = Column(String(255), nullable=False)
    encrypt_public_key = Column(Text, nullable=True)  # 用于大模型api_key加密
    plan = Column(
        String(255),
        nullable=False,
        server_default=text("'basic'::character varying"),
    )
    custom_config = Column(JSONB, nullable=True)

    tenant_user_joins = relationship(
        "TenantUserJoin",
        back_populates="tenant",
    )

    users = association_proxy("tenant_user_joins", "user")

    model_provider_tenant_joins = relationship(
        "ModelProviderTenantJoin", back_populates="tenant", overlaps="tenant"
    )

    model_providers = relationship(
        "ModelProvider",
        secondary="model_provider_tenant_join",
        back_populates="tenants",
        overlaps="model_provider_tenant_joins",
    )
