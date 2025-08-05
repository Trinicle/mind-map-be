from typing import List, Optional
from pydantic import BaseModel, Field


class Content(BaseModel):
    speaker: Optional[str] = None
    text: Optional[str] = None


class Topic(BaseModel):
    title: Optional[str] = None
    content: List[Content] = Field(default_factory=list)
    connected_topics: List[str] = Field(default_factory=list)


class TranscriptState(BaseModel):
    file_path: str
    quality_check: Optional[int] = None
    transcript: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    topics: List[Topic] = Field(default_factory=list)
