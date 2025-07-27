from typing import List, Optional, TypedDict
from datetime import datetime

from src.models import MindMap
from .client import supabase
from .auth import get_user


def insert_mindmap(
    title: str,
    description: str,
    date: str,
    tags: List[str] = [],
) -> MindMap:
    """
    Insert a new mindmap for the current user.
    The user_id will be automatically set to auth.uid() by Supabase's RLS policies.
    """
    # Convert ISO string to datetime
    parsed_date = datetime.fromisoformat(date.replace("Z", "+00:00"))

    data = {
        "title": title,
        "description": description,
        "tags": tags,
        "date": parsed_date.isoformat(),  # Convert back to ISO format for Postgres
    }

    # We don't need to explicitly set user_id as it's handled by RLS
    result = supabase.table("MindMap").insert(data).execute()

    return result.data[0] if result.data else None


def get_user_mindmaps() -> List[MindMap]:
    """
    Get all mindmaps for the current user.
    RLS policies will automatically filter to show only the current user's mindmaps.
    """
    result = supabase.table("MindMap").select("*").execute()
    return result.data if result.data else []


def get_mindmap(mindmap_id: str) -> Optional[MindMap]:
    """
    Get a specific mindmap by ID.
    RLS policies will ensure users can only access their own mindmaps.
    """
    result = (
        supabase.table("MindMap").select("*").eq("id", mindmap_id).limit(1).execute()
    )
    return result.data[0] if result.data else None
