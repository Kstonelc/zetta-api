from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from uuid import UUID
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    name = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    status = Column(String(32), nullable=False)
    secret = Column(String(32), nullable=True)  # 用于邮箱验证的验证码

    tenant_user_joins = relationship(
        "TenantUserJoin",
        back_populates="user",
        passive_deletes=True,
    )
    # 源关系 目标字段
    tenants = relationship(
        "Tenant",
        secondary="tenant_user_join",
        viewonly=True,
        back_populates="users",
        overlaps="tenant_user_joins,users",
    )

    # 虚拟属性
    @property
    def current_tenant(self):
        for join in self.tenant_user_joins:
            if join.current:
                return join.tenant
        return None

    def get_role(self, tenant_id: str):
        for join in self.tenant_user_joins:
            if str(join.tenant_id) == tenant_id:
                return join.role
        return None
