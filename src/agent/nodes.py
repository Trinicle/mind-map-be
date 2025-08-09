from typing import List
from dotenv import load_dotenv
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.tools.retriever import create_retriever_tool
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel
from src.agent.connection import get_redis_history, get_vectorstore
from src.agent.tools import tools
from src.agent.prompts import ChatBotPrompts, MindMapPrompts
from src.agent.state import ChatBotState, Content, Topic, TranscriptState

load_dotenv()
llm = ChatOpenAI(model="gpt-5-nano", temperature=1, max_completion_tokens=500)

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200


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


def split_transcript_node(state: TranscriptState):
    transcript = state.transcript
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return {"transcript_chunks": text_splitter.split_text(transcript)}


def identify_participants_node(state: TranscriptState):
    transcript_chunks = state.transcript_chunks
    structured_llm = llm.with_structured_output(ParticipantsOutput)
    participants = set()
    for chunk in transcript_chunks:
        messages = [
            SystemMessage(content=MindMapPrompts.IDENTIFY_PARTICIPANTS_SYSTEM),
            HumanMessage(content=MindMapPrompts.identify_participants_prompt(chunk)),
        ]
        response = structured_llm.invoke(messages)
        participants.update(response.participants)

    return {"participants": list(participants)}


def identify_topics_node(state: TranscriptState):
    transcript_chunks = state.transcript_chunks
    structured_llm = llm.with_structured_output(TopicsOutput)

    topics_dict = {}

    for chunk in transcript_chunks:
        messages = [
            SystemMessage(content=MindMapPrompts.IDENTIFY_TOPICS_SYSTEM),
            HumanMessage(content=MindMapPrompts.identify_topics_prompt(chunk)),
        ]
        response = structured_llm.invoke(messages)
        chunk_topics = response.topics

        for new_topic in chunk_topics:
            if new_topic.title not in topics_dict:
                topics_dict[new_topic.title] = new_topic
            else:
                existing_topic = topics_dict[new_topic.title]

                existing_content_set = set()
                for content in existing_topic.content:
                    content_id = f"{content.speaker}:{content.text}"
                    existing_content_set.add(content_id)

                for new_content in new_topic.content:
                    content_id = f"{new_content.speaker}:{new_content.text}"
                    if content_id not in existing_content_set:
                        existing_topic.content.append(new_content)
                        existing_content_set.add(content_id)

                existing_connected = set(existing_topic.connected_topics)
                for connected_topic in new_topic.connected_topics:
                    if connected_topic not in existing_connected:
                        existing_topic.connected_topics.append(connected_topic)
                        existing_connected.add(connected_topic)

    return {"topics": list(topics_dict.values())}


def query_node(state: ChatBotState):
    """
    Process the user's query with conversation history from Redis.
    Returns AI message with potential tool calls.
    """
    config = {
        "configurable": {
            "session_id": state.conversation_id,
        },
        "metadata": {
            "user_id": state.user_id,
            "transcript_id": state.transcript_id,
            "conversation_id": state.conversation_id,
        },
    }

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", ChatBotPrompts.CHATBOT_SYSTEM),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    filters = {
        "user_id": state.user_id,
    }

    if state.transcript_id:
        filters["transcript_id"] = state.transcript_id

    with get_vectorstore() as vectorstore:
        retriever = vectorstore.as_retriever(
            search_kwargs={
                "k": 3,
                "filter": filters,
            }
        )
        retriever_tool = create_retriever_tool(
            retriever,
            name="transcript_retriever",
            description="A tool that can retrieve information from the transcript",
        )

        all_tools = [retriever_tool] + tools
        llm_with_tools = llm.bind_tools(all_tools)

        chain = prompt | llm_with_tools

        with get_redis_history(state.conversation_id) as redis_history:
            llm_with_history = RunnableWithMessageHistory(
                chain,
                get_session_history=redis_history,
                input_messages_key="input",
                history_messages_key="history",
            )

            latest_message = state.messages[-1]
            user_input = latest_message.content

            return {
                "messages": [
                    llm_with_history.invoke({"input": user_input}, config=config)
                ]
            }


def response_node(state: ChatBotState):
    """Process tool results and generate final AI response"""
    config = {
        "configurable": {},
        "metadata": {
            "user_id": state.user_id,
            "transcript_id": state.transcript_id,
            "conversation_id": state.conversation_id,
        },
    }

    tool_messages = [
        msg for msg in state.messages if getattr(msg, "type", "") == "tool"
    ]

    if not tool_messages:
        return {"messages": []}

    synthesis_prompt = SystemMessage(
        content="""You are a helpful assistant. Based on the tool results and conversation history, 
        provide a clear, helpful response to the user. Synthesize the information from the tools 
        into a natural, conversational response."""
    )

    context_messages = [synthesis_prompt] + state.messages

    return {"messages": [llm.invoke(context_messages, config=config)]}
