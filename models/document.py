from openai.types.conversations import TextContent
from sqlalchemy import Column, Integer, String, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel


class Document(BaseModel):
    __tablename__ = "document"
    __table_args__ = Index("index_document_wiki_id_status", "wiki_id", "status")

    wiki_id = Column(UUID, ForeignKey("wiki.id"), nullable=False)
    source_uri = Column(String, nullable=False)
    title = Column(String, nullable=False)
    status = Column(Integer, nullable=False)
    hash = Column(String, nullable=True)
    metadata = Column(JSONB, nullable=True)


class ParentChunk(BaseModel):
    __tablename__ = "parent_chunk"
    __table_args__ = (
        # 新增复合索引：优先按 wiki_id 过滤/分组/排序，同时加速 (wiki_id, document_id) 联合查询
        Index("index_parent_chunk_wiki_id_document_id", "wiki_id", "document_id"),
        Index("index_parent_chunk_wiki_id", "wiki_id"),
    )

    document_id = Column(UUID, ForeignKey("document.id"), nullable=False)
    wiki_id = Column(UUID, ForeignKey("wiki.id"), nullable=False)
    index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)


class ChildChunk(BaseModel):
    __tablename__ = "child_chunk"

    parent_id = Column(UUID, ForeignKey("parent_chunk.id"), nullable=False)
    document_id = Column(UUID, ForeignKey("document.id"), nullable=False)
    wiki_id = Column(UUID, ForeignKey("wiki.id"), nullable=False)
