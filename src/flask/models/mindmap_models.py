from datetime import datetime
from typing import List
from pydantic import BaseModel


class MindMap(BaseModel):
    id: str
    user_id: str
    title: str
    participants: List[str]
    description: str
    created_at: datetime
    date: datetime


class MindMapWithTags(MindMap):
    tags: List[str]


class MindMapPostRequest(BaseModel):
    title: str
    description: str
    date: datetime
    tags: List[str]
    file_path: str


class MindMapResponse(BaseModel):
    id: str
    title: str
    description: str
    date: datetime
    tags: List[str]
