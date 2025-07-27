from datetime import datetime
from src.models import Content
from .client import supabase


def insert_content(text: str, date: datetime, topic_id: str) -> Content | None:
    """
    Insert a new content for the current user.
    """
    data = {
        "text": text,
        "date": date,
        "topic_id": topic_id,
    }

    result = supabase.table("Content").insert(data).execute()
    return result.data[0] if result.data else None
