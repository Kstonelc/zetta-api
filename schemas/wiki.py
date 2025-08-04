from pydantic import BaseModel, EmailStr, constr
from uuid import UUID
from typing import Optional


class WikiCreateRequest(BaseModel):
    wikiName: str
    wikiDesc: Optional[str] = None
    wikiType: int
    wikiEmbeddingId: UUID
    wikiRerankId: UUID
    wikiSimThresh: float
