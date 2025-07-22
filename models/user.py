from sqlalchemy import Column, Integer, String
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    avatar = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    secret = Column(String, nullable=True)  # 用于邮箱验证的密钥
