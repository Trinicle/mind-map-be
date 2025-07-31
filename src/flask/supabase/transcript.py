from flask import Request
from src.flask.models.transcript_models import Transcript
from .client import get_client


def insert_transcript(request: Request, text: str) -> Transcript:
    """
    Insert a new content for the current user.
    """
    data = {
        "text": text,
    }

    client = get_client(request)
    result = client.table("Transcript").insert(data).execute()
    return result.data[0] if result.data else None
