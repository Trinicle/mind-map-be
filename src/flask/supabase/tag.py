from typing import List
from flask import Request

from src.flask.models.tag_model import Tag, TagResponse
from src.flask.supabase.client import get_async_client, get_client


def get_tags(request: Request) -> List[TagResponse]:
    """
    Get all tags for the current user.
    """
    client = get_client(request)

    request_name = request.args.get("name")
    if request_name:
        result = (
            client.table("Tags")
            .select("name")
            .like("name", f"%{request_name}%")
            .execute()
        )
    else:
        result = client.table("Tags").select("id, name").execute()

    data = result.data if result.data else []
    return [TagResponse(name=tag["name"]) for tag in data]


def insert_tags(request: Request, tags: List[str], mindmap_id: str) -> List[Tag]:
    client = get_client(request)
    try:
        data = [{"name": tag, "mindmap_id": mindmap_id} for tag in tags]
        result = client.table("Tags").insert(data).execute()
        data = result.data if result.data else []
        return [
            Tag(
                id=tag["id"],
                user_id=tag["user_id"],
                name=tag["name"],
                mindmap_id=mindmap_id,
                created_at=tag["created_at"],
            )
            for tag in data
        ]
    except Exception as e:
        print(e)
        return []


async def insert_tags_async(
    request: Request, tags: List[str], mindmap_id: str
) -> List[Tag]:
    client = await get_async_client(request)
    try:
        data = [{"name": tag, "mindmap_id": mindmap_id} for tag in tags]
        result = await client.table("Tags").insert(data).execute()
        data = result.data if result.data else []
        tags_list = [
            Tag(
                id=tag["id"],
                user_id=tag["user_id"],
                name=tag["name"],
                mindmap_id=mindmap_id,
                created_at=tag["created_at"],
            )
            for tag in data
        ]
        return tags_list
    except Exception as e:
        print(e)
        return []
