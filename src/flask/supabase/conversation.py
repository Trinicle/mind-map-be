from typing import List, Optional
from flask import Request
from src.flask.models.conversation_models import Conversation
from .client import get_client


def create_conversation(
    request: Request, transcript_id: Optional[str] = None, title: Optional[str] = None
) -> Conversation:
    """Create a new conversation for the current user."""
    data = {
        "transcript_id": transcript_id,
        "title": title or "New Conversation",
    }

    try:
        client = get_client(request)
        result = client.table("conversations").insert(data).execute()
        data = result.data[0] if result.data else None
        return Conversation(
            id=data["id"],
            user_id=data["user_id"],
            transcript_id=data["transcript_id"],
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )
    except Exception as e:
        print(f"Error creating conversation: {e}")
        raise e


def get_conversation(request: Request, conversation_id: str) -> Optional[Conversation]:
    """Get a conversation by ID for the current user."""
    try:
        client = get_client(request)
        result = (
            client.table("conversations")
            .select("*")
            .eq("id", conversation_id)
            .execute()
        )

        if not result.data:
            return None

        data = result.data[0]
        return Conversation(
            id=data["id"],
            user_id=data["user_id"],
            transcript_id=data["transcript_id"],
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )
    except Exception as e:
        print(f"Error getting conversation: {e}")
        return None


def get_user_conversations(request: Request) -> List[Conversation]:
    """Get all conversations for the current user."""
    try:
        client = get_client(request)
        result = (
            client.table("conversations")
            .select("*")
            .order("updated_at", desc=True)
            .execute()
        )

        conversations = []
        for data in result.data:
            conversations.append(
                Conversation(
                    id=data["id"],
                    user_id=data["user_id"],
                    transcript_id=data["transcript_id"],
                    title=data["title"],
                    created_at=data["created_at"],
                    updated_at=data["updated_at"],
                )
            )

        return conversations
    except Exception as e:
        print(f"Error getting user conversations: {e}")
        return []


def update_conversation_title(
    request: Request, conversation_id: str, title: str
) -> Optional[Conversation]:
    """Update a conversation's title."""
    try:
        client = get_client(request)
        result = (
            client.table("conversations")
            .update({"title": title})
            .eq("id", conversation_id)
            .execute()
        )

        if not result.data:
            return None

        data = result.data[0]
        return Conversation(
            id=data["id"],
            user_id=data["user_id"],
            transcript_id=data["transcript_id"],
            title=data["title"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )
    except Exception as e:
        print(f"Error updating conversation: {e}")
        return None
