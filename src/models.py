from datetime import datetime
from enum import Enum
from typing import List
from gotrue import TypedDict


class ContentAgentOutput(TypedDict):
    text: str
    date: datetime


class ContentDetail(TypedDict):
    id: str
    topic_id: str
    user_id: str
    text: str
    date: datetime
    created_at: datetime
    updated_at: datetime


class TopicAgentOutput(TypedDict):
    title: str
    content: List[ContentAgentOutput]


class ConnectionAgentOutput(TypedDict):
    from_topic: str
    to_topic: str
    reason: str


class MindMapAgentOutput(TypedDict):
    participants: List[str]
    topics: List[TopicAgentOutput]
    connections: List[ConnectionAgentOutput]


class MindMapDetailResponse(TypedDict):
    id: str
    user_id: str
    title: str
    tags: List[str]
    participants: List[str]
    description: str
    created_at: datetime
    date: datetime


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
