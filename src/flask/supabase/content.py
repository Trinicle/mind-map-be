from flask import Request
from src.flask.models.content_models import Content
from .client import get_client, get_async_client


def insert_content(
    request: Request, text: str, speaker: str, topic_id: str
) -> Content | None:
    """
    Insert a new content for the current user.
    """
    data = {
        "text": text,
        "speaker": speaker,
        "topic_id": topic_id,
    }

    client = get_client(request)
    result = client.table("Content").insert(data).execute()
    return result.data[0] if result.data else None


async def insert_content_async(
    request: Request, text: str, speaker: str, topic_id: str
) -> Content | None:
    """
    Insert a new content for the current user (async version).
    """
    data = {
        "text": text,
        "speaker": speaker,
        "topic_id": topic_id,
    }

    client = await get_async_client(request)
    result = await client.table("Content").insert(data).execute()
    return result.data[0] if result.data else None
