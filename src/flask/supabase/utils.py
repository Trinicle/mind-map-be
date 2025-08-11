import asyncio
from typing import List
from flask import Request
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_redis import RedisChatMessageHistory
from src.agent.connection import get_checkpoint, get_redis_client
from src.agent.state import TranscriptState
from src.flask.models.conversation_models import ChatMessageResponse
from src.flask.models.mindmap_models import MindMapResponse
from src.flask.supabase.mindmap import insert_mindmap_async
from src.flask.supabase.question import insert_questions_async
from src.flask.supabase.tag import insert_tags_async
from src.flask.supabase.topic import insert_topic_with_content_async
from src.flask.supabase.transcript import (
    get_transcript,
    insert_transcript_as_vector_async,
    insert_transcript_async,
)

llm = ChatOpenAI(model="gpt-5-nano", temperature=1)


async def insert_transcript_data_async(
    request: Request,
    transcript_state: TranscriptState,
    title: str,
    description: str,
    date: str,
    tags: List[str],
):
    participants = transcript_state.participants
    topics = transcript_state.topics
    transcript = transcript_state.transcript
    questions = transcript_state.questions

    transcript_result = await insert_transcript_async(request, transcript)
    transcript_id = transcript_result.id
    tasks = [
        insert_transcript_as_vector_async(request, transcript, transcript_id),
        insert_mindmap_async(
            request, title, description, date, participants, transcript_id
        ),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Check if any tasks failed and handle accordingly
    vector_result, mindmap_result = results

    if isinstance(vector_result, Exception):
        print(f"Vector insertion failed: {vector_result}")
        # Continue execution - vector insertion failure is not critical

    if isinstance(mindmap_result, Exception):
        print(f"Mindmap insertion failed: {mindmap_result}")
        raise mindmap_result  # Re-raise since mindmap is critical

    mindmap = mindmap_result
    tags_result, questions_result = await asyncio.gather(
        insert_tags_async(request, tags, mindmap.id),
        insert_questions_async(request, questions, mindmap.id),
    )

    topic_tasks = []
    for topic in topics:
        connected_topics = topic.connected_topics
        topic_task = insert_topic_with_content_async(
            request, topic, connected_topics, mindmap.id, topic.content
        )
        topic_tasks.append(topic_task)

    await asyncio.gather(*topic_tasks, return_exceptions=True)

    return MindMapResponse(
        id=mindmap.id,
        title=mindmap.title,
        description=mindmap.description,
        date=mindmap.date,
        tags=[tag.name for tag in tags_result],
    )


async def load_conversation_history(conversation_id: str):
    history = []

    with get_redis_client() as redis_client:
        redis_history = RedisChatMessageHistory(
            session_id=conversation_id, redis_client=redis_client
        )

        existing = redis_history
        if existing:
            return [
                ChatMessageResponse(
                    message=msg.content,
                    type=msg.type,
                    id=msg.additional_kwargs["id"],
                ).model_dump()
                for msg in existing.messages
                if msg.type not in ["tool", "system"]
                and (
                    hasattr(msg, "additional_kwargs")
                    and msg.additional_kwargs.get("tool_calls") is None
                )
            ]

        config = {"configurable": {"thread_id": conversation_id}}
        with get_checkpoint() as checkpoint:
            state = checkpoint.get(config)
            messages: List[BaseMessage] = state.get("channel_values", {}).get(
                "messages", []
            )

        for msg in messages:
            if msg.type not in ["tool", "system"] and (
                hasattr(msg, "additional_kwargs")
                and msg.additional_kwargs.get("tool_calls") is None
            ):
                msg.additional_kwargs["id"] = msg.id
                redis_history.add_message(msg)
                history.append(
                    ChatMessageResponse(
                        message=msg.content,
                        type=msg.type,
                        id=msg.id,
                    ).model_dump()
                )
    return history
