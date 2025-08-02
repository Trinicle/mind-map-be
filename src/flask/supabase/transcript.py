from flask import Request
from src.flask.models.transcript_models import Transcript
from .client import get_client, get_client_from_auth_token


def insert_transcript(auth_token: str, text: str) -> Transcript:
    """
    Insert a new content for the current user.
    """
    data = {
        "text": text,
    }

    client = get_client_from_auth_token(auth_token)
    result = client.table("Transcript").insert(data).execute()
    return result.data[0] if result.data else None
