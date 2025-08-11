from typing import List
from datetime import datetime
from flask import Request

from src.flask.models.mindmap_models import MindMap, MindMapResponse, MindMapWithTags
from .client import get_async_client, get_client


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
        created_at=data["created_at"],
        date=data["date"],
    )


async def insert_mindmap_async(
    request: Request,
    title: str,
    description: str,
    date: str,
    participants: List[str] = [],
    transcript_id: str = None,
) -> MindMap:
    parsed_date = datetime.fromisoformat(date.replace("Z", "+00:00"))

    data = {
        "title": title,
        "description": description,
        "date": parsed_date.isoformat(),
        "participants": participants,
        "transcript_id": transcript_id,
    }
    client = await get_async_client(request)
    result = await client.table("MindMap").insert(data).execute()
    data = result.data[0] if result.data else None

    return MindMap(
        id=data["id"],
        user_id=data["user_id"],
        title=data["title"],
        participants=data["participants"],
        description=data["description"],
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
    filter = {}

    if title:
        filter["input_title"] = title
    if tags:
        filter["input_tags"] = tags
    if date:
        filter["input_date"] = date.isoformat()

    result = client.rpc("get_mindmaps_with_tags_by_filter", filter).execute()
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
    return MindMapWithTags(
        id=data["id"],
        user_id=data["user_id"],
        title=data["title"],
        participants=data["participants"],
        description=data["description"],
        tags=data["tags"],
        created_at=data["created_at"],
        date=data["date"],
    )
