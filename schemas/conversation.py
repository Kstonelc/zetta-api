from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ConversationCreateRequest(BaseModel):
    tenantId: UUID
    userId: UUID


class ConversationQueryRequest(BaseModel):
    tenantId: UUID
    userId: UUID
    conversationStatus: Optional[int] = None


class ConversationMessageQueryRequest(BaseModel):
    conversationId: UUID


class ConversationMessageCreateRequest(BaseModel):
    conversationId: UUID
    userContent: str
    assistantContent: Optional[str] = None
