from chromadb import HttpClient
from chromadb.api.models import Collection
from config import settings
from loguru import logger


class ChromaWrapper:
    def __init__(
        self,
        host: str = settings.VECTOR_DB_HOST,
        port: int = settings.VECTOR_DB_PORT,
        collection_name: str = "",
    ):
        if not collection_name:
            raise ValueError(
                "Parameter 'collection_name' is required and cannot be empty."
            )
        self.client = HttpClient(host=host, port=port)
        self.collection = self._get_or_create_collection(collection_name)

    def ping(self):
        try:
            print(self.client.list_collections())
            return True
        except Exception as e:
            logger.error("[ChromaWrapper connect failed]:", e)
            return False

    def _get_or_create_collection(self, name: str) -> Collection:
        return self.client.get_or_create_collection(name)

    def add(self, doc_id: str, content: str, embedding: list):
        self.collection.add(ids=[doc_id], documents=[content], embeddings=[embedding])

    def query(self, embedding: list, top_k: int = 10):
        return self.collection.query(query_embeddings=[embedding], n_results=top_k)

    def delete(self, doc_id: str):
        self.collection.delete(ids=[doc_id])

    def edit(self, doc_id: str, content: str, embedding: list):
        self.collection.update(
            ids=[doc_id], documents=[content], embeddings=[embedding]
        )
