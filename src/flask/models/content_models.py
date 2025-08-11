from datetime import datetime
from pydantic import BaseModel


class Content(BaseModel):
    id: str
    topic_id: str
    user_id: str
    speaker: str
    text: str
    created_at: datetime
    updated_at: datetime


class BasicContent(BaseModel):
    id: str
    speaker: str
    text: str
