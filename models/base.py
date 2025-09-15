from sqlalchemy import Column, Boolean, DateTime, func, text, inspect
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    __abstract__ = True  # 不会创建表，只作为继承用

    id: Mapped[str] = mapped_column(
        UUID, primary_key=True, server_default=text("uuid_generate_v4()")
    )  # server_default 需要pgsql服务器端支持UUID
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def to_dict(self):
        return {
            column.key: getattr(self, column.key)
            for column in inspect(self).mapper.columns
        }
