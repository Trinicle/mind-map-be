import asyncio
from typing import List
from flask import Request
from langchain_redis import RedisChatMessageHistory
from src.agent.connection import get_checkpoint, get_redis_client
from src.agent.state import TranscriptState
from src.flask.models.conversation_models import ChatMessageResponse
from src.flask.models.mindmap_models import MindMapResponse
from src.flask.supabase.mindmap import insert_mindmap_async
from src.flask.supabase.tag import insert_tags_async
from src.flask.supabase.topic import insert_topic_with_content_async
from src.flask.supabase.transcript import (
    insert_transcript_as_vector_async,
    insert_transcript_async,
)


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

    transcript_result = await insert_transcript_async(request, transcript)
    transcript_id = transcript_result.id

    tasks = [
        insert_transcript_as_vector_async(request, transcript, transcript_id),
        insert_mindmap_async(
            request, title, description, date, participants, transcript_id
        ),
    ]
    _, mindmap = await asyncio.gather(*tasks, return_exceptions=True)

    tags_result = await insert_tags_async(request, tags, mindmap.id)

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
        tags=[tag.name for tag in tags],
    )


async def load_conversation_history(conversation_id: str):
    config = {"configurable": {"thread_id": conversation_id}}
    history = []
    with get_checkpoint() as checkpoint:
        state = checkpoint.get(config)
        messages = state.get("channel_values", {}).get("messages", [])

    with get_redis_client() as redis_client:
        redis_history = RedisChatMessageHistory(
            session_id=conversation_id, redis_client=redis_client
        )

        redis_history.clear()
        for msg in messages:
            if msg.type not in ["tool", "system"]:
                redis_history.add_message(msg)

                message = ChatMessageResponse(
                    message=msg.content,
                    type=msg.type,
                    id=msg.id,
                ).model_dump()
                history.append(message)

    return history
