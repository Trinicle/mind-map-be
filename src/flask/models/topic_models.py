from datetime import datetime
from typing import List
from pydantic import BaseModel


class Topic(BaseModel):
    id: str
    mindmap_id: str
    user_id: str
    title: str
    updated_at: datetime
    created_at: datetime
    connected_topics: List[str]


class GetTopicsRequest(BaseModel):
    mindmap_id: str


class GetTopicsResponse(BaseModel):
    data: List[Topic]
