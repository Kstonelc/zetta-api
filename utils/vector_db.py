"""
@File        : utils/vector_db.py
@Description : Vector DB 数据库封装
@Author      : Kstone
@Date        : 2025/07/11
"""

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.models import Distance, VectorParams
from typing import List, Dict, Optional
import threading


class VectorWrapper:
    _instance = None
    _lock = threading.Lock()

    def __new__(
        cls,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "default",
        vector_dim: int = 768,  # 根据模型选择
    ):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._init_client(host, port, collection_name, vector_dim)
        return cls._instance

    def _init_client(self, host, port, collection_name, vector_dim):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name

        # 创建 collection（如不存在）
        if self.collection_name not in self.client.get_collections().collections:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
            )

    def ping(self):
        self.client.get_collections()

    def insert(self, points: List[Dict]):
        """
        插入数据，格式：
        [
            {
                "id": "uuid",
                "vector": [...],
                "payload": {"text": "...", "source": "..."}
            },
            ...
        ]
        """
        self.client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(**p) for p in points],
        )

    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        filter_payload: Optional[Dict] = None,
    ):
        """
        搜索最近向量，支持 payload 条件过滤
        """
        filter_obj = None
        if filter_payload:
            filter_obj = Filter(
                must=[
                    FieldCondition(key=k, match=MatchValue(value=v))
                    for k, v in filter_payload.items()
                ]
            )
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=filter_obj,
        )

    def delete_by_id(self, point_id: str):
        self.client.delete(
            collection_name=self.collection_name, points_selector={"points": [point_id]}
        )

    def update(self, point_id: str, new_vector: List[float], new_payload: Dict):
        # Qdrant 没有 "update" API，用删除 + 重新添加实现
        self.delete_by_id(point_id)
        self.insert([{"id": point_id, "vector": new_vector, "payload": new_payload}])


vector_client = VectorWrapper()
