from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel
from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    PrimaryKeyConstraint,
    UniqueConstraint,
    Boolean,
    String,
)


class ModelProviderTenantJoin(BaseModel):
    __tablename__ = "model_provider_tenant_join"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="model_provider_tenant_join_pkey"),
        Index("model_provider_tenant_join_model_provider_id_idx", "model_provider_id"),
        Index("model_provider_tenant_join_tenant_id_idx", "tenant_id"),
        UniqueConstraint(
            "tenant_id", "model_provider_id", name="unique_model_provider_tenant_join"
        ),
    )

    tenant_id = Column(
        UUID,
        ForeignKey("tenant.id", ondelete="SET NULL"),
        nullable=True,
    )
    model_provider_id = Column(
        UUID,
        ForeignKey("model_provider.id", ondelete="SET NULL"),
        nullable=True,
    )

    tenant = relationship(
        "Tenant",
        back_populates="tenant_model_provider_joins",
        overlaps="model_providers",
    )
    model_provider = relationship(
        "ModelProvider",
        back_populates="tenant_model_provider_joins",
        overlaps="tenants",
    )


class TenantUserJoin(BaseModel):
    __tablename__ = "tenant_user_join"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="tenant_user_join_pkey"),
        Index("tenant_user_join_account_id_idx", "user_id"),
        Index("tenant_user_join_tenant_id_idx", "tenant_id"),
        UniqueConstraint("tenant_id", "user_id", name="unique_tenant_user_join"),
    )

    tenant_id = Column(
        UUID, ForeignKey("tenant.id", ondelete="SET NULL"), nullable=True
    )
    user_id = Column(UUID, ForeignKey("user.id", ondelete="SET NULL"), nullable=True)
    current = Column(
        Boolean, nullable=False, server_default="false"
    )  # 当前用户激活的租户
    role = Column(String(16), nullable=False, server_default="normal")
    invited_by = Column(UUID, nullable=True)

    tenant = relationship(
        "Tenant",
        back_populates="tenant_user_joins",
        overlaps="users, tenants",
    )
    user = relationship(
        "User",
        back_populates="tenant_user_joins",
        overlaps="users,tenants",
    )
