import datetime
from typing import List, TypedDict

from src.flask.models.topic_models import TopicAgentOutput


class MindMap(TypedDict):
    id: str
    user_id: str
    title: str
    participants: List[str]
    description: str
    created_at: datetime
    date: datetime


class ConnectionAgentOutput(TypedDict):
    from_topic: str
    to_topic: str
    reason: str


class MindMapAgentOutput(TypedDict):
    participants: List[str]
    topics: List[TopicAgentOutput]
    connections: List[ConnectionAgentOutput]


class MindMapPostRequest(TypedDict):
    title: str
    description: str
    date: datetime
    tags: List[str]
    file_path: str


class MindMapResponse(TypedDict):
    id: str
    title: str
    description: str
    date: datetime
    tags: List[str]
