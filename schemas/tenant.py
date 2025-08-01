from uuid import UUID
from pydantic import BaseModel
from typing import Optional


class TenantQueryRequest(BaseModel):
    tenantId: Optional[UUID] = None
