from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class Conversation(BaseModel):
    id: str
    user_id: str
    transcript_id: Optional[str] = None
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationCreateRequest(BaseModel):
    transcript_id: Optional[str] = None
    query: str


class ChatMessage(BaseModel):
    conversation_id: str
    message: str


class ChatMessageResponse(BaseModel):
    id: str
    message: str
    type: str
