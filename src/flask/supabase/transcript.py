from src.flask.models.transcript_models import Transcript
from .client import supabase


def insert_transcript(text: str) -> Transcript:
    """
    Insert a new content for the current user.
    """
    data = {
        "text": text,
    }

    result = supabase.table("Transcript").insert(data).execute()
    return result.data[0] if result.data else None
