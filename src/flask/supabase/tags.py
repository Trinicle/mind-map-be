from typing import List
from flask import Request

from src.flask.supabase.client import get_client


def get_tags(request: Request) -> List[str]:
    """
    Get all tags for the current user.
    """
    client = get_client(request)

    request_name = request.args.get("name")
    result = (
        client.table("Tags").select("name").like("name", f"%{request_name}%").execute()
    )
    return result.data if result.data else []


def insert_tags(request: Request, tags: List[str]) -> List[str]:
    client = get_client(request)
    result = client.table("Tags").insert(tags).execute()
    return result.data if result.data else []
