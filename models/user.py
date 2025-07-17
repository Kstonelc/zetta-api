from sqlalchemy import Column, Integer, String
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
