import datetime
from typing import TypedDict


class ContentAgentOutput(TypedDict):
    text: str


class Content(TypedDict):
    id: str
    topic_id: str
    user_id: str
    text: str
    created_at: datetime
    updated_at: datetime
