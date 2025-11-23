"""
@File        : utils/vector_db.py
@Description : Vector DB 数据库封装
@Author      : Kstone
@Date        : 2025/07/11
"""

from typing import List, Dict, Optional
import threading

from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.models import Distance, VectorParams
from qdrant_client.http.exceptions import UnexpectedResponse

from config import settings


class VectorWrapper:
    _instance = None
    _lock = threading.Lock()

    def __new__(
        cls,
        host: str = settings.VECTOR_DB_HOST,
        port: int = settings.VECTOR_DB_PORT,
        collection_name: str = "default",
        vector_dim: int = 768,  # 根据模型维度选择
    ):
        # 这里的单例只保证“进程内”唯一，多 worker（多进程）各自一份没关系
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._init_client(host, port, collection_name, vector_dim)
        return cls._instance

    def _init_client(self, host, port, collection_name, vector_dim):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.vector_dim = vector_dim

        # 幂等地确保 collection 存在，在多 worker 场景下不会打架
        self._ensure_collection()

    def _ensure_collection(self):
        """
        幂等创建 collection：
        - 已存在：直接返回
        - 不存在（404）：尝试 create_collection
        - 并发创建导致的 409：忽略，当作成功
        """
        # 1. 先判断是否存在
        try:
            self.client.get_collection(self.collection_name)
            return  # 已存在，直接返回
        except UnexpectedResponse as e:
            status = getattr(e, "status_code", None)
            if status != 404:
                # 不是“没找到”的错误，直接抛出去
                raise

        # 2. 尝试创建（可能跟其它 worker 并发）
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_dim,
                    distance=Distance.COSINE,
                ),
            )
        except UnexpectedResponse as e:
            status = getattr(e, "status_code", None)
            msg = str(e)
            # 如果是并发导致的 already exists，就当作成功
            if not (status == 409 and "already exists" in msg):
                raise

    def ping(self):
        # 这里仅用于“连通性检查”，不会触发建库
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
            collection_name=self.collection_name,
            points_selector={"points": [point_id]},
        )

    def update(self, point_id: str, new_vector: List[float], new_payload: Dict):
        # Qdrant 没有 "update" API，用删除 + 重新添加实现
        self.delete_by_id(point_id)
        self.insert([{"id": point_id, "vector": new_vector, "payload": new_payload}])


vector_client = VectorWrapper()
