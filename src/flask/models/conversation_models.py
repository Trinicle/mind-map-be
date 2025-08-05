from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class Conversation(BaseModel):
    id: str
    user_id: str
    transcript_id: Optional[str] = None
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ConversationCreateRequest(BaseModel):
    transcript_id: Optional[str] = None
    title: Optional[str] = None
    initial_message: Optional[str] = None


class ChatMessage(BaseModel):
    conversation_id: str
    message: str
    transcript_id: Optional[str] = None
