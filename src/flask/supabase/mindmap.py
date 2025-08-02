from typing import List
from datetime import datetime
from flask import Request

from src.flask.models.mindmap_models import MindMap, MindMapResponse
from .client import get_client


def insert_mindmap(
    request: Request,
    title: str,
    description: str,
    date: str,
    participants: List[str] = [],
    transcript_id: str = None,
) -> MindMap:
    """
    Insert a new mindmap for the current user.
    """
    client = get_client(request)

    # Convert ISO string to datetime
    parsed_date = datetime.fromisoformat(date.replace("Z", "+00:00"))

    data = {
        "title": title,
        "description": description,
        "date": parsed_date.isoformat(),  # Convert back to ISO format for Postgres
        "participants": participants,
        "transcript_id": transcript_id,
    }

    # We don't need to explicitly set user_id as it's handled by RLS
    result = client.table("MindMap").insert(data).execute()

    return result.data[0] if result.data else None


def get_user_mindmaps(request: Request) -> List[MindMapResponse]:
    """
    Get all mindmaps for the current user.
    """
    client = get_client(request)
    result = client.rpc("get_mindmaps_with_tags").execute()

    return result.data if result.data else []


def get_user_mindmaps_by_query(
    request: Request, title: str = None, tags: List[str] = None, date: str = None
) -> List[MindMapResponse]:
    """
    Get all mindmaps for the current user by query.
    """
    client = get_client(request)
    select = client.table("MindMap").select("id, title, description, tags, date")

    if title:
        select = select.eq("title", title)
    if tags:
        select = select.contains("tags", tags)
    if date:
        select = select.eq("date", date)

    result = select.execute()
    return result.data if result.data else []


def get_mindmap_detail(request: Request, mindmap_id: str) -> MindMap | None:
    """
    Get a specific mindmap by ID.
    """
    client = get_client(request)
    result = client.table("MindMap").select("*").eq("id", mindmap_id).limit(1).execute()
    return result.data[0] if result.data else None
