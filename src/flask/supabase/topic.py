from flask import Request
from src.flask.models.topic_models import Topic


def insert_topic(request: Request, title: str, mindmap_id: str) -> Topic | None:
    """
    Insert a new topic for the current user.
    """
    data = {
        "title": title,
        "mindmap_id": mindmap_id,
    }

    client = get_client(request)
    result = client.table("Topic").insert(data).execute()
    return result.data[0] if result.data else None
