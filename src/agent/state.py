from typing import List, Optional
from pydantic import BaseModel, Field
from typing import Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage


class ContentState(BaseModel):
    speaker: Optional[str] = None
    text: Optional[str] = None


class TopicState(BaseModel):
    title: Optional[str] = None
    content: List[ContentState] = Field(default_factory=list)
    connected_topics: List[str] = Field(default_factory=list)


class TranscriptState(BaseModel):
    file: bytes
    quality_check: Optional[int] = None
    transcript_chunks: List[str] = Field(default_factory=list)
    transcript: Optional[str] = None
    participants: List[str] = Field(default_factory=list)
    topics: List[TopicState] = Field(default_factory=list)


class ChatBotState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages]
