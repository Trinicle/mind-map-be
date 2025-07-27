from typing import List
from datetime import datetime

from src.models import MindMapDetailResponse, MindMapResponse
from .client import supabase


def insert_mindmap(
    title: str,
    description: str,
    date: str,
    tags: List[str] = [],
    participants: List[str] = [],
) -> MindMapDetailResponse:
    """
    Insert a new mindmap for the current user.
    """
    # Convert ISO string to datetime
    parsed_date = datetime.fromisoformat(date.replace("Z", "+00:00"))

    data = {
        "title": title,
        "description": description,
        "tags": tags,
        "date": parsed_date.isoformat(),  # Convert back to ISO format for Postgres
        "participants": participants,
    }

    # We don't need to explicitly set user_id as it's handled by RLS
    result = supabase.table("MindMap").insert(data).execute()

    return result.data[0] if result.data else None


def get_user_mindmaps() -> List[MindMapResponse]:
    """
    Get all mindmaps for the current user.
    """
    result = (
        supabase.table("MindMap").select("id, title, description, tags, date").execute()
    )
    return result.data if result.data else []


def get_mindmap_detail(mindmap_id: str) -> MindMapDetailResponse | None:
    """
    Get a specific mindmap by ID.
    """
    result = (
        supabase.table("MindMap").select("*").eq("id", mindmap_id).limit(1).execute()
    )
    return result.data[0] if result.data else None
