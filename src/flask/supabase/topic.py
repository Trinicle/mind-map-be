from flask import Request
from src.flask.models.topic_models import Topic
from src.flask.supabase.client import get_client, get_async_client


def get_topics(request: Request, mindmap_id: str) -> list[Topic]:
    """
    Get all topics for the current user.
    """
    client = get_client(request)
    result = client.table("Topic").select("*").eq("mindmap_id", mindmap_id).execute()
    return result.data if result.data else []


def insert_topic(
    request: Request, title: str, connected_topics: list[str], mindmap_id: str
) -> Topic | None:
    """
    Insert a new topic for the current user.
    """
    data = {
        "title": title,
        "mindmap_id": mindmap_id,
        "connected_topics": connected_topics,
    }

    client = get_client(request)
    result = client.table("Topic").insert(data).execute()
    return result.data[0] if result.data else None


async def insert_topic_async(
    request: Request, title: str, connected_topics: list[str], mindmap_id: str
) -> Topic | None:
    """
    Insert a new topic for the current user (async version).
    """
    data = {
        "title": title,
        "mindmap_id": mindmap_id,
        "connected_topics": connected_topics,
    }

    client = await get_async_client(request)
    result = await client.table("Topic").insert(data).execute()
    return result.data[0] if result.data else None
