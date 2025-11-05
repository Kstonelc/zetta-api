from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class ConversationChatRequest(BaseModel):
    promptText: str
    modelName: str
    modelProvider: str
    assistantMessageId: UUID


class ConversationCreateRequest(BaseModel):
    tenantId: UUID
    userId: UUID


class ConversationQueryRequest(BaseModel):
    tenantId: Optional[UUID] = None
    userId: Optional[UUID] = None
    conversationId: Optional[UUID] = None
    conversationStatus: Optional[List[int]] = None


class ConversationMessageQueryRequest(BaseModel):
    conversationId: UUID


class ConversationMessageCreateRequest(BaseModel):
    conversationId: UUID
    userContent: str
    assistantContent: Optional[str] = None


class ConversationMessageUpdateRequest(BaseModel):
    messageId: UUID
    assistantContent: Optional[str] = None
