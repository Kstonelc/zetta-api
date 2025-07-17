from pydantic import BaseModel
from typing import Optional


class ModelProviderQueryRequest(BaseModel):
    modelProviderId: Optional[int] = None


class ModelProviderAddRequest(BaseModel):
    modelProviderName: str
    modelProviderDesc: Optional[str] = None


class ModelProviderUpdateRequest(BaseModel):
    modelProviderApiKey: Optional[str] = None
    modelProviderId: int


class ModelAddRequest(BaseModel):
    modelName: str
    modelDisplayName: Optional[str] = None
    modelProviderId: int
    modelApiKey: Optional[str] = None
    modelMaxContextTokens: Optional[int] = None
    modelTokenLimit: Optional[int] = None


class ModelQueryRequest(BaseModel):
    modelProviderId: Optional[int] = None
