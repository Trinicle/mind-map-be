from typing import TypedDict


class Tag(TypedDict):
    id: str
    user_id: str
    name: str
    mindmap_id: str
    created_at: str


class TagResponse(TypedDict):
    name: str
