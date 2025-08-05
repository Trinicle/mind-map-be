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
        "date": parsed_date.isoformat(),
        "participants": participants,
        "transcript_id": transcript_id,
    }

    result = client.table("MindMap").insert(data).execute()
    data = result.data[0] if result.data else None

    return MindMap(
        id=data["id"],
        user_id=data["user_id"],
        title=data["title"],
        participants=data["participants"],
        description=data["description"],
        tags=data["tags"],
        created_at=data["created_at"],
        date=data["date"],
    )


def get_user_mindmaps(request: Request) -> List[MindMapResponse]:
    """
    Get all mindmaps for the current user.
    """
    client = get_client(request)
    result = client.rpc("get_mindmaps_with_tags").execute()
    data = result.data if result.data else []
    return [
        MindMapResponse(
            id=mindmap["id"],
            title=mindmap["title"],
            description=mindmap["description"],
            tags=mindmap["tags"],
            date=mindmap["date"],
        )
        for mindmap in data
    ]


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
    data = result.data if result.data else []
    return [
        MindMapResponse(
            id=mindmap["id"],
            title=mindmap["title"],
            description=mindmap["description"],
            tags=mindmap["tags"],
            date=mindmap["date"],
        )
        for mindmap in data
    ]


def get_mindmap_detail(request: Request, mindmap_id: str) -> MindMap:
    """
    Get a specific mindmap by ID.
    """
    client = get_client(request)
    result = client.rpc(
        "get_mindmap_with_tags_by_id", {"input_id": mindmap_id}
    ).execute()
    data = result.data[0] if result.data else None
    print(data)
    return MindMap(
        id=data["id"],
        user_id=data["user_id"],
        title=data["title"],
        participants=data["participants"],
        description=data["description"],
        tags=data["tags"],
        created_at=data["created_at"],
        date=data["date"],
    )
