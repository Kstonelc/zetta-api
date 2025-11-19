from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from .base import BaseModel


class Wiki(BaseModel):
    __tablename__ = "wiki"

    name = Column(String, nullable=False)
    type = Column(Integer, nullable=False)  # 结构化数据和非结构化数据
    embedding_id = Column(UUID, ForeignKey("model.id"))  # 嵌入模型ID
    rerank_id = Column(UUID, ForeignKey("model.id"))
    tenant_id = Column(UUID, nullable=False)
    user_id = Column(UUID, nullable=False)
    desc = Column(String, nullable=True)

    # 不建立相互的外键管理 单方面的
    embedding_model = relationship(
        "Model", foreign_keys=[embedding_id], backref="used_for_embedding"
    )
    rerank_model = relationship(
        "Model", foreign_keys=[rerank_id], backref="used_for_rerank"
    )
