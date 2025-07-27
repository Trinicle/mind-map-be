from datetime import datetime
from enum import Enum
from typing import List
from gotrue import TypedDict
from werkzeug.datastructures import FileStorage


class MindMap(TypedDict):
    title: str
    description: str
    date: datetime
    tags: List[str]
    file_path: str


class MindMapResponse(TypedDict):
    id: str
    user_id: str
    title: str
    description: str
    date: datetime
    tags: List[str]
    created_at: datetime


class Topic(TypedDict):
    id: str
    mindmap_id: str
    user_id: str
    title: str
    updated_at: datetime
    created_at: datetime
    related_topics: List[str]


class GetTopicsRequest(TypedDict):
    mindmap_id: str


class GetTopicsResponse(TypedDict):
    data: List[Topic]
