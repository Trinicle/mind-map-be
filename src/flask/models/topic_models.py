import datetime
from typing import List, TypedDict
from src.flask.models.content_models import ContentAgentOutput


class TopicAgentOutput(TypedDict):
    title: str
    content: List[ContentAgentOutput]


class Topic(TypedDict):
    id: str
    mindmap_id: str
    user_id: str
    title: str
    updated_at: datetime
    created_at: datetime
    connected_topics: List[str]


class GetTopicsRequest(TypedDict):
    mindmap_id: str


class GetTopicsResponse(TypedDict):
    data: List[Topic]
