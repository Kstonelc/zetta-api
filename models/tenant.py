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
        nullable=True,
        server_default=text("'basic'::character varying"),
    )
    custom_config = Column(JSONB, nullable=True)

    """
    back_populates: 这个关系在对方模型的反向属性名
    passive_deletes: 在数据库层面会自己删除 不会触发 ORM 操作
    """
    tenant_user_joins = relationship(
        "TenantUserJoin",
        back_populates="tenant",
        passive_deletes=True,
    )

    users = relationship(
        "User",
        secondary="tenant_user_join",
        viewonly=True,
        back_populates="tenants",
        overlaps="tenant_user_joins,tenants",
    )

    model_provider_tenant_joins = relationship(
        "ModelProviderTenantJoin", back_populates="tenant", passive_deletes=True,
    )

    model_providers = relationship(
        "ModelProvider",
        secondary="model_provider_tenant_join",
        viewonly=True,
        back_populates="tenants",
        overlaps="model_provider_tenant_joins, tenants",
    )
