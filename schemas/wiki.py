from pydantic import BaseModel, EmailStr, constr
from uuid import UUID
from typing import Optional


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
