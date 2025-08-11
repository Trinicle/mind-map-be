from datetime import datetime
from pydantic import BaseModel


class Question(BaseModel):
    id: str
    mindmap_id: str
    user_id: str
    question: str
    created_at: datetime
    updated_at: datetime
