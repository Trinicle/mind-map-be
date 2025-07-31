from src.flask.models.topic_models import Topic
from .client import supabase


def insert_topic(title: str, mindmap_id: str) -> Topic | None:
    """
    Insert a new topic for the current user.
    """
    data = {
        "title": title,
        "mindmap_id": mindmap_id,
    }

    result = supabase.table("Topic").insert(data).execute()
    return result.data[0] if result.data else None
