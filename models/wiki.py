from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from .base import BaseModel


class Wiki(BaseModel):
    __tablename__ = "wiki"

    name = Column(String, nullable=False)
    type = Column(Integer, nullable=False)  # 结构化数据和非结构化数据
    embedding_id = Column(Integer, ForeignKey("embedding.id"))  # 嵌入模型ID
    rerank_id = Column(Integer, ForeignKey("rerank.id"))
    sim_thresh = Column(Float, nullable=False)  # 相似度阈值
    user_id = Column(Integer, ForeignKey("users.id"))  # 创建者ID
    desc = Column(String, nullable=True)

    # embedding = relationship("Embedding")
    # rerank = relationship("Rerank")
    # user = relationship("User")
