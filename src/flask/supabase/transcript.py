from flask import Request
from src.flask.models.transcript_models import Transcript
from .client import get_client, get_client_from_auth_token


def insert_transcript(request: Request, text: str) -> Transcript:
    """
    Insert a new content for the current user.
    """
    data = {
        "text": text,
    }

    try:
        client = get_client(request)
        result = client.table("Transcript").insert(data).execute()
        data = result.data[0] if result.data else None
        return Transcript(
            id=data["id"],
            user_id=data["user_id"],
            text=data["text"],
        )
    except Exception as e:
        print(f"Error inserting transcript: {e}")
        print(f"Error type: {type(e)}")
        if hasattr(e, "details"):
            print(f"Error details: {e.details}")
        raise e


def get_transcript(request: Request, mindmap_id: str) -> Transcript:
    """
    Get the transcript for the current user.
    """
    client = get_client(request)
    result = client.rpc(
        "get_transcript_by_mindmap_id", {"input_id": mindmap_id}
    ).execute()
    data = result.data[0] if result.data else None
    return Transcript(
        id=data["id"],
        user_id=data["user_id"],
        text=data["text"],
    )
