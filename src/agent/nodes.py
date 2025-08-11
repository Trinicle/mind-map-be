import asyncio
from io import BytesIO
from typing import List
from dotenv import load_dotenv
from langchain_unstructured.document_loaders import UnstructuredLoader
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from src.agent.prompts import MindMapPrompts
from src.agent.state import TopicState, TranscriptState

load_dotenv()
llm = ChatOpenAI(model="gpt-5-nano", temperature=1)

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200


class QuestionsOutput(BaseModel):
    questions: List[str] = Field(default_factory=list)


class QualityCheckOutput(BaseModel):
    quality_check: int


class ParticipantsOutput(BaseModel):
    participants: List[str]


class TopicsOutput(BaseModel):
    topics: List[TopicState]


def load_transcript_node(state: TranscriptState):
    file = state.file
    file_name = state.file_name
    bytes_io = BytesIO(file)

    loader = UnstructuredLoader(file=bytes_io, metadata_filename=file_name)

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


def split_transcript_node(state: TranscriptState):
    transcript = state.transcript
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return {"transcript_chunks": text_splitter.split_text(transcript)}


async def identify_participants_node(state: TranscriptState):
    transcript_chunks = state.transcript_chunks
    structured_llm = llm.with_structured_output(ParticipantsOutput)

    async def process_chunk(chunk):
        messages = [
            SystemMessage(content=MindMapPrompts.IDENTIFY_PARTICIPANTS_SYSTEM),
            HumanMessage(content=MindMapPrompts.identify_participants_prompt(chunk)),
        ]
        response = await structured_llm.ainvoke(messages)
        return response.participants

    tasks = [process_chunk(chunk) for chunk in transcript_chunks]
    chunk_results = await asyncio.gather(*tasks)

    participants = set()
    for chunk_participants in chunk_results:
        participants.update(chunk_participants)

    return {"participants": list(participants)}


async def identify_topics_node(state: TranscriptState):
    transcript = state.transcript
    structured_llm = llm.with_structured_output(TopicsOutput)

    messages = [
        SystemMessage(content=MindMapPrompts.IDENTIFY_TOPICS_SYSTEM),
        HumanMessage(content=MindMapPrompts.identify_topics_prompt(transcript)),
    ]
    response = await structured_llm.ainvoke(messages)
    topics = response.topics

    return {"topics": topics}


async def create_questions_node(state: TranscriptState):
    transcript = state.transcript
    structured_llm = llm.with_structured_output(QuestionsOutput)

    messages = [
        SystemMessage(content=MindMapPrompts.CREATE_QUESTIONS_SYSTEM),
        HumanMessage(content=MindMapPrompts.create_questions_prompt(transcript)),
    ]
    response = await structured_llm.ainvoke(messages)

    return {"questions": response.questions}
