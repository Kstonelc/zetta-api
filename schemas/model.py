from uuid import UUID
from pydantic import BaseModel
from typing import Optional, List
from enums import ModelProviderUpdateType, ModelType


class ModelProviderQueryRequest(BaseModel):
    tenantId: Optional[UUID] = None
    modelProviderId: Optional[UUID] = None


class ModelProviderAddRequest(BaseModel):
    modelProviderName: str
    modelProviderDesc: Optional[str] = None


class ModelProviderUpdateRequest(BaseModel):
    modelProviderUpdateType: ModelProviderUpdateType
    modelProviderApiKey: Optional[str] = None
    modelProviderId: UUID


class ModelAddRequest(BaseModel):
    modelName: str
    modelDisplayName: Optional[str] = None
    modelProviderId: UUID
    modelMaxContextTokens: Optional[int] = None
    modelTokenLimit: Optional[int] = None


class ModelQueryRequest(BaseModel):
    modelType: ModelType
    tenantId: Optional[UUID] = None


class ModelUpdateRequest(BaseModel):
    modelId: UUID
    active: Optional[bool] = None
