from uuid import UUID
from pydantic import BaseModel
from typing import Optional


class ModelProviderQueryRequest(BaseModel):
    tenantId: Optional[UUID] = None
    modelProviderId: Optional[UUID] = None


class ModelProviderCreateRequest(BaseModel):
    modelProviderName: str
    modelProviderDesc: Optional[str] = None


class ModelProviderUpdateRequest(BaseModel):
    modelProviderUpdateType: int
    modelProviderApiKey: Optional[str] = None
    modelProviderId: UUID


class ModelCreateRequest(BaseModel):
    modelName: str
    modelDisplayName: Optional[str] = None
    modelProviderId: UUID
    modelMaxContextTokens: Optional[int] = None
    modelTokenLimit: Optional[int] = None


class ModelQueryRequest(BaseModel):
    modelType: int
    tenantId: Optional[UUID] = None


class ModelUpdateRequest(BaseModel):
    modelId: UUID
    active: Optional[bool] = None
