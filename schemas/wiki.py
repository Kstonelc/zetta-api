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


class WikiQueryRequest(BaseModel):
    tenantId: UUID


class WikiPreviewFileChunkRequest(BaseModel):
    filePath: str
    chunkType: int
    chunkSize: Optional[int] = None
    chunkOverlap: Optional[int] = None
    parentChunkSize: Optional[int] = None
    parentChunkOverlap: Optional[int] = None
    childChunkSize: Optional[int] = None
    childChunkOverlap: Optional[int] = None


class WikiIndexDocumentRequest(BaseModel):
    filesPath: List[str]
    wikiId: UUID
    chunkType: int
    parentChunkSize: Optional[int] = None
    parentChunkOverlap: Optional[int] = None
    childChunkSize: Optional[int] = None
    childChunkOverlap: Optional[int] = None


class WikiIndexProgressRequest(BaseModel):
    fileNames: List[str]
    wikiId: UUID


class WikiRecallDocsRequest(BaseModel):
    wikiName: str
    queryContent: str
