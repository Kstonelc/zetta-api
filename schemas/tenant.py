from uuid import UUID
from pydantic import BaseModel
from typing import Optional


class TenantQueryRequest(BaseModel):
    tenantId: UUID


class TenantUpdateRequest(BaseModel):
    tenantId: UUID
    tenantName: Optional[str] = None
