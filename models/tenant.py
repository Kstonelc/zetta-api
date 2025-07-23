from sqlalchemy import (
    Column,
    String,
    Text,
    text,
    Boolean,
    JSON,
    Index,
    ForeignKey,
    UniqueConstraint,
    PrimaryKeyConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel
from enums import UserStatus


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
        passive_deletes=True,
        overlaps="users",
    )

    # secondary="tenant_user_join"--> join表:tenant_user_join
    users = relationship(
        "User",
        secondary="tenant_user_join",
        back_populates="tenants",
        overlaps="tenant_user_joins",
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
        UUID, ForeignKey("tenant.id", ondelete="SET NULL"), nullable=False
    )
    user_id = Column(UUID, ForeignKey("user.id", ondelete="SET NULL"), nullable=False)
    current = Column(
        Boolean, nullable=False, server_default="false"
    )  # 当前用户激活的租户
    role = Column(String(16), nullable=False, server_default="normal")
    invited_by = Column(UUID, nullable=True)

    tenant = relationship(
        "Tenant", back_populates="tenant_user_joins", overlaps="users, tenants"
    )
    user = relationship(
        "User", back_populates="tenant_user_joins", overlaps="users,tenants"
    )
