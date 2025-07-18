from pydantic import BaseModel
from typing import Optional, List
from enums import ModelProviderUpdateType


class ModelProviderQueryRequest(BaseModel):
    modelProviderId: Optional[int] = None


class ModelProviderAddRequest(BaseModel):
    modelProviderName: str
    modelProviderDesc: Optional[str] = None


class ModelProviderUpdateRequest(BaseModel):
    modelProviderUpdateType: ModelProviderUpdateType
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


class ModelUpdateRequest(BaseModel):
    modelId: int
    active: Optional[bool] = None
