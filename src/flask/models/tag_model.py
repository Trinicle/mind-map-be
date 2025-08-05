from pydantic import BaseModel


class Tag(BaseModel):
    id: str
    user_id: str
    name: str
    mindmap_id: str
    created_at: str


class TagResponse(BaseModel):
    name: str
