from pydantic import BaseModel, EmailStr, constr
from uuid import UUID
from typing import Optional, List, Dict


class WikiCreateRequest(BaseModel):
    wikiName: str
    wikiDesc: Optional[str] = None
    wikiType: int
    tenantId: UUID
    userId: UUID
    wikiEmbeddingId: UUID
    wikiRerankId: UUID
    wikiSimThresh: float


class WikiQueryRequest(BaseModel):
    tenantId: UUID


class WikiPreviewFileChunkRequest(BaseModel):
    filePath: str
    chunkSize: int
    chunkOverlap: int


class WikiIndexFileRequest(BaseModel):
    chunks: List[Dict]


class WikiRecallDocsRequest(BaseModel):
    wikiName: str
    queryContent: str
