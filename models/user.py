from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import BaseModel
from .tenant import Tenant, TenantUserJoin


class User(BaseModel):
    __tablename__ = "user"

    name = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    status = Column(String(32), nullable=False)
    secret = Column(String(32), nullable=True)  # 用于邮箱验证的密钥

    tenant_user_joins = relationship(
        "TenantUserJoin",
        back_populates="user",
        overlaps="tenants",
    )

    tenants = relationship(
        "Tenant",
        secondary="tenant_user_join",
        back_populates="users",
        overlaps="tenant_user_joins",
        cascade="all, delete-orphan",
    )

    # 虚拟属性
    @property
    def current_tenant(self):
        for join in self.tenant_user_joins:
            if join.current and join.active:
                return join.tenant
        return None
