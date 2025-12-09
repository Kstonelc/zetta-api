from openai.types.conversations import TextContent
from sqlalchemy import Column, Integer, String, ForeignKey, Index, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel


class Document(BaseModel):
    __tablename__ = "document"

    chunk_type = Column(Integer, nullable=False, default=0)
    size = Column(Integer, nullable=False, default=0)
    source_uri = Column(String, nullable=False)
    title = Column(String, nullable=False)
    status = Column(Integer, nullable=False)
    hash = Column(String, nullable=True)
    extra_metadata = Column(JSONB, nullable=True)
    node_id = Column(UUID, ForeignKey("node.id"), nullable=True)

    node = relationship("Node", back_populates="doc_info")


class Node(BaseModel):
    __tablename__ = "node"

    name = Column(String, nullable=False)  # 文件或文件夹的名字
    parent_id = Column(UUID, ForeignKey("node.id"), nullable=True)  # 父节点ID
    is_folder = Column(Boolean, nullable=False)  # 是否为文件夹
    wiki_id = Column(UUID, ForeignKey("wiki.id"), nullable=False)

    parent = relationship(
        "Node", remote_side=lambda: [Node.id], back_populates="children"
    )
    children = relationship(
        "Node", back_populates="parent", cascade="all, delete-orphan"
    )

    doc_info = relationship("Document", back_populates="node", uselist=False)


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
    index_in_parent = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding_status = Column(Integer, nullable=False)
    vector_point_id = Column(Text, nullable=True)


# 文件索引任务
class DocumentIndexTask(BaseModel):
    __tablename__ = "document_index_task"

    wiki_id = Column(UUID, ForeignKey("wiki.id"), nullable=False)
    file_name = Column(String, nullable=False, default="")
    status = Column(Integer, nullable=False)
    total_chunks = Column(Integer, nullable=True)
    processed_chunks = Column(Integer, nullable=True)
    current_phase = Column(Integer, nullable=True)  # 当前阶段
    error_message = Column(Text, nullable=True)
