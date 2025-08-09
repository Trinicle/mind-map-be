import os
from typing import List
from flask import Request
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.flask.models.transcript_models import Transcript
from .client import get_auth_token, get_client
from src.agent.tools import get_vectorstore

load_dotenv()

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200


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


def insert_transcript_as_vector(request: Request, text: str, transcript_id: str):
    chunks = _chunk_transcript(text)
    client = get_client(request)
    auth_token = get_auth_token(request)
    user_id = client.auth.get_user(auth_token).user.id

    metadata = {
        "transcript_id": transcript_id,
        "user_id": user_id,
    }

    with get_vectorstore() as vectorstore:
        vectorstore.add_texts(chunks, metadatas=[metadata] * len(chunks))


def _chunk_transcript(text: str) -> List[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return text_splitter.split_text(text)


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
