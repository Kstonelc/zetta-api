from sqlalchemy import Column, Integer, Boolean, DateTime, func
from .db import Base


class BaseModel(Base):
    __abstract__ = True  # 不会创建表，只作为继承用

    id = Column(Integer, primary_key=True, index=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    # created_by = Column(Integer, nullable=False)
    # updated_by = Column(Integer, nullable=False)
