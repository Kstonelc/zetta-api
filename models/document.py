from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import relationship
from .base import BaseModel


class Document(BaseModel):
    __tablename__ = "document"

    name = Column(String(255), nullable=False, unique=True, default="")
    size = Column(Integer, nullable=False)  # 文件大小
    mode = Column(String(255), nullable=False)  # 分段模式
    type = Column(String(255), nullable=False)  # 文件类型
    status = Column(Integer, nullable=False)  # 文件状态
    wiki_id = Column(UUID(as_uuid=True), ForeignKey("wiki.id"), nullable=False)
