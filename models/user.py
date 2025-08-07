from sqlalchemy import Column, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from .base import BaseModel


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
    )
    # 源关系 目标字段
    tenants = association_proxy("tenant_user_joins", "tenant")

    # 虚拟属性
    @property
    def current_tenant(self):
        for join in self.tenant_user_joins:
            if join.current and join.active:
                return join.tenant
        return None

    def get_role(self, tenant_id):
        for join in self.tenant_user_joins:
            if join.tenant_id == tenant_id:
                return join.role
        return None
