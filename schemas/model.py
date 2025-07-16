from pydantic import BaseModel
from typing import Optional


class ModelProviderAddRequest(BaseModel):
    modelProviderName: str
    modelProviderDesc: Optional[str] = None


class ModelAddRequest(BaseModel):
    modelName: str
    modelDisplayName: Optional[str] = None
    modelProviderId: int
    modelApiKey: Optional[str] = None
    modelMaxContextTokens: Optional[int] = None
    modelTokenLimit: Optional[int] = None
