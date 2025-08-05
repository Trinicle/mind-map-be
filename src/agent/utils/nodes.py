import re
from typing import List
from dotenv import load_dotenv
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from src.agent.utils.prompts import MindMapPrompts
from src.agent.utils.state import Content, Topic, TranscriptState

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


class QualityCheckOutput(BaseModel):
    quality_check: int


class ParticipantsOutput(BaseModel):
    participants: List[str]


class TopicsOutput(BaseModel):
    topics: List[Topic]


def load_transcript_node(state: TranscriptState):
    file_path = state.file_path

    extension = file_path.split(".")[-1]

    loader = None
    if extension == "docx":
        loader = UnstructuredWordDocumentLoader(file_path)
    else:
        loader = TextLoader(file_path)

    documents = loader.load()

    content = "\n".join([doc.page_content for doc in documents])
    return {"transcript": content}


def clean_transcript_node(state: TranscriptState):
    transcript = state.transcript
    messages = [
        SystemMessage(content=MindMapPrompts.CLEAN_TRANSCRIPT_SYSTEM),
        HumanMessage(content=MindMapPrompts.clean_transcript_prompt(transcript)),
    ]

    cleaned_transcript = llm.invoke(messages)
    return {"transcript": cleaned_transcript.content}


def quality_check_node(state: TranscriptState):
    transcript = state.transcript
    messages = [
        SystemMessage(content=MindMapPrompts.QUALITY_CHECK_SYSTEM),
        HumanMessage(content=MindMapPrompts.quality_check_prompt(transcript)),
    ]
    structured_llm = llm.with_structured_output(QualityCheckOutput)
    result = structured_llm.invoke(messages)
    return {"quality_check": result.quality_check}


def quality_score_condition_node(state: TranscriptState):
    quality_check = state.quality_check
    if quality_check < 7:
        return "reclean"
    else:
        return "pass"


def identify_participants_node(state: TranscriptState):
    transcript = state.transcript

    structured_llm = llm.with_structured_output(ParticipantsOutput)

    messages = [
        SystemMessage(content=MindMapPrompts.IDENTIFY_PARTICIPANTS_SYSTEM),
        HumanMessage(content=MindMapPrompts.identify_participants_prompt(transcript)),
    ]

    result = structured_llm.invoke(messages)
    return {"participants": result.participants}


def identify_topics_node(state: TranscriptState):
    transcript = state.transcript

    structured_llm = llm.with_structured_output(TopicsOutput)

    messages = [
        SystemMessage(content=MindMapPrompts.IDENTIFY_TOPICS_SYSTEM),
        HumanMessage(content=MindMapPrompts.identify_topics_prompt(transcript)),
    ]

    result = structured_llm.invoke(messages)

    return {"topics": result.topics}
