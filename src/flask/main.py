import os
import asyncio
import atexit
from typing import List
from flask import Flask, Request, request, jsonify
from gotrue import Session
from src.agent.utils.graph import transcript_graph
from src.agent.utils.state import TranscriptState, ChatBotState
from src.agent.utils.chatbot import initialize_chatbot
from src.agent.utils.connection import get_checkpoint, close_connection_pool
from langchain_core.messages import HumanMessage
from src.flask.models.mindmap_models import MindMapResponse
from src.flask.models.topic_models import Topic
from src.flask.supabase.auth import (
    UserModel,
    refresh_session,
    signin,
    signout,
    signup,
)
from flask_cors import CORS
from gotrue.errors import AuthApiError
from gotrue.types import AuthResponse

from src.flask.supabase.client import get_auth_token, get_client
from src.flask.supabase.content import insert_content_async
from src.flask.supabase.mindmap import (
    get_mindmap_detail,
    get_user_mindmaps,
    get_user_mindmaps_by_query,
    insert_mindmap,
)
from src.flask.supabase.tag import get_tags, insert_tags_async
from src.flask.supabase.topic import get_topics, insert_topic_async
import json
from datetime import datetime

from src.flask.supabase.transcript import (
    get_transcript,
    insert_transcript,
    insert_transcript_as_vector,
)
from src.agent.utils.tools import get_messages_vectorstore
from src.flask.supabase.conversation import (
    create_conversation,
    get_conversation,
    get_user_conversations,
)
from src.flask.models.conversation_models import (
    ChatMessageResponse,
    ConversationCreateRequest,
    ChatMessage,
)

UPLOAD_FOLDER = "uploads"

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:4200"],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "PUT", "POST", "DELETE", "OPTIONS"],
)

# Register cleanup function to close connection pools on app shutdown
atexit.register(close_connection_pool)


def serialize_auth_response(response: AuthResponse):
    return {
        "user": response.user.model_dump(mode="json"),
        "session": response.session.model_dump(mode="json"),
    }


def serialize_session(session: Session):
    return {
        "session": session.model_dump(mode="json"),
    }


@app.route("/auth/signup", methods=["POST"])
def handle_signup():
    try:
        data: UserModel = request.json
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        response = signup(data)
        serialized_response = serialize_auth_response(response)
        return jsonify({"message": "Authenticated", "data": serialized_response}), 200
    except AuthApiError as e:
        exception = e.to_dict()
        return (
            jsonify({"message": exception["message"], "code": exception["code"]}),
            exception["status"],
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/auth/signin", methods=["POST"])
def handle_signin():
    try:
        data: UserModel = request.json
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400
        response = signin(email, password)
        serialized_response = serialize_auth_response(response)
        return jsonify({"message": "Authenticated", "data": serialized_response}), 200
    except AuthApiError as e:
        exception = e.to_dict()
        return (
            jsonify({"message": exception["message"], "code": exception["code"]}),
            exception["status"],
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/auth/signout", methods=["POST"])
def handle_signout():
    try:
        signout(request)
        return jsonify({"message": "Logged out"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/auth/refresh", methods=["POST"])
def handle_session():
    try:
        data = request.json
        refresh_token = data.get("refresh_token")
        response = refresh_session(request, refresh_token)
        serialized_response = serialize_auth_response(response)
        return jsonify({"message": "Session found", "data": serialized_response}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/dashboard/mindmap", methods=["GET"])
def handle_mindmap_get():
    try:
        cards = get_user_mindmaps(request)
        # Convert Pydantic models to dictionaries for JSON serialization
        serialized_cards = [card.model_dump() for card in cards]
        return (
            jsonify({"message": "Mindmap cards found", "data": serialized_cards}),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/dashboard/mindmap/search", methods=["GET"])
def handle_mindmap_search():
    try:
        request_tags = request.args.get("tags")
        request_title = request.args.get("title")
        request_date = request.args.get("date")
        date = (
            datetime.fromisoformat(request_date.replace("Z", "+00:00"))
            if request_date
            else None
        )
        cards = get_user_mindmaps_by_query(request, request_title, request_tags, date)
        # Convert Pydantic models to dictionaries for JSON serialization
        serialized_cards = [card.model_dump() for card in cards]
        return (
            jsonify({"message": "Mindmap cards found", "data": serialized_cards}),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/dashboard/mindmap/<mindmap_id>", methods=["GET"])
def handle_mindmap_detail(mindmap_id: str):
    try:
        mindmap = get_mindmap_detail(request, mindmap_id)
        # Convert Pydantic model to dictionary for JSON serialization
        serialized_mindmap = mindmap.model_dump()
        return (
            jsonify({"message": "Mindmap detail found", "data": serialized_mindmap}),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/dashboard/mindmap/tags", methods=["GET"])
def handle_mindmap_tags():
    try:
        tags = get_tags(request)
        # Convert Pydantic models to dictionaries for JSON serialization
        serialized_tags = [tag.model_dump() for tag in tags]
        return jsonify({"message": "Mindmap tags found", "data": serialized_tags}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/dashboard/mindmap", methods=["POST"])
def handle_mindmap_create():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"message": "File is required"}), 400

        title = request.form.get("title")
        description = request.form.get("description")
        date = request.form.get("date")
        tags = json.loads(request.form.get("tags", "[]"))

        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        transcript_state = TranscriptState(
            file_path=file_path,
        )

        result: TranscriptState = transcript_graph.invoke(transcript_state)

        os.remove(file_path)

        participants = result.participants
        topics = result.topics

        transcript = insert_transcript(request, result.transcript)
        transcript_id = transcript.id
        insert_transcript_as_vector(request, result.transcript, transcript_id)

        mindmap = insert_mindmap(
            request, title, description, date, participants, transcript_id
        )
        if mindmap is None:
            return jsonify({"message": "Failed to create mindmap"}), 400
        print("inserted mindmap")

        async def insert_data_async():
            tasks = []

            tags_task = insert_tags_async(request, tags, mindmap.id)
            tasks.append(tags_task)

            topic_tasks = []
            for topic in topics:
                connected_topics = topic.connected_topics
                topic_task = insert_topic_with_content_async(
                    request,
                    topic,
                    connected_topics,
                    mindmap.id,
                )
                topic_tasks.append(topic_task)

            tags_result = await tags_task
            topics_results = await asyncio.gather(*topic_tasks, return_exceptions=True)

            return tags_result, topics_results

        async def insert_topic_with_content_async(
            request: Request,
            topic_data: Topic,
            connected_topics: List[str],
            mindmap_id: str,
        ):
            topic = await insert_topic_async(
                request, topic_data.title, connected_topics, mindmap_id
            )
            print("inserted topic")
            if topic is None:
                return None

            content_tasks = []
            for content_item in topic_data.get("content", []):
                if content_item and content_item.get("text"):
                    content_task = insert_content_async(
                        request,
                        content_item.text,
                        content_item.speaker,
                        topic.id,
                    )
                    content_tasks.append(content_task)

            if content_tasks:
                await asyncio.gather(*content_tasks, return_exceptions=True)
                print("inserted content for topic")

            return topic

        tags, topics_results = asyncio.run(insert_data_async())

        response = MindMapResponse(
            id=mindmap.id,
            title=mindmap.title,
            description=mindmap.description,
            date=mindmap.date,
            tags=[tag.name for tag in tags],
        )

        return (
            jsonify({"message": "Mindmap created", "data": response.model_dump()}),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/mindmap/<mindmap_id>", methods=["GET"])
def handle_mindmap_get_detail(mindmap_id: str):
    try:
        mindmap = get_mindmap_detail(request, mindmap_id)
        serialized_mindmap = mindmap.model_dump()
        return (
            jsonify({"message": "Mindmap detail found", "data": serialized_mindmap}),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/mindmap/<mindmap_id>/topics", methods=["GET"])
def handle_mindmap_topics(mindmap_id: str):
    try:
        topics = get_topics(request, mindmap_id)
        # Convert Pydantic models to dictionaries for JSON serialization
        serialized_topics = [topic.model_dump() for topic in topics]
        return (
            jsonify({"message": "Mindmap topics found", "data": serialized_topics}),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/mindmap/<mindmap_id>/transcript", methods=["GET"])
def handle_transcript_get_detail(mindmap_id: str):
    try:
        transcript = get_transcript(request, mindmap_id)
        # Convert Pydantic model to dictionary for JSON serialization
        serialized_transcript = transcript.model_dump()
        return (
            jsonify(
                {"message": "Transcript detail found", "data": serialized_transcript}
            ),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/conversations", methods=["POST"])
def handle_create_conversation():
    """Create a new conversation"""
    try:
        data = request.json or {}
        conversation_request = ConversationCreateRequest(**data)

        conversation = create_conversation(request, conversation_request.transcript_id)

        return (
            jsonify(
                {
                    "message": "Conversation created successfully",
                    "data": conversation.model_dump(),
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error creating conversation: {e}")
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/conversations", methods=["GET"])
def handle_get_conversations():
    """Get all conversations for the current user"""
    try:
        conversations = get_user_conversations(request)
        return jsonify({"data": [conv.model_dump() for conv in conversations]}), 200
    except Exception as e:
        print(f"Error getting conversations: {e}")
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/conversations/<conversation_id>/history", methods=["GET"])
def handle_get_conversation_history(conversation_id: str):
    """Get conversation history (last 10 messages)"""
    try:
        conversation = get_conversation(request, conversation_id)
        if not conversation:
            return jsonify({"message": "Conversation not found"}), 404

        config = {"configurable": {"thread_id": conversation_id}}

        checkpoint = get_checkpoint()
        state = checkpoint.get(config)
        messages = state.get("channel_values", {}).get("messages", [])

        history = [
            ChatMessageResponse(
                message=(
                    msg.content if isinstance(msg.content, str) else str(msg.content)
                ),
                type=msg.type,
                id=msg.id,
            ).model_dump()
            for msg in messages[-10:]
            if msg.type != "tool" and msg.type != "system"
        ]

        return (
            jsonify({"message": "Conversation history found", "data": history}),
            200,
        )

    except Exception as e:
        print(f"Error getting conversation history: {e}")
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/chat", methods=["POST"])
def handle_send_message():
    """Handle chat messages with conversation persistence"""
    try:
        data = request.json
        chat_request = ChatMessage(**data)

        conversation = get_conversation(request, chat_request.conversation_id)
        if not conversation:
            return jsonify({"message": "Conversation not found"}), 404

        client = get_client(request)
        auth_token = get_auth_token(request)

        user_id = client.auth.get_user(auth_token).user.id

        read_config = {"configurable": {"thread_id": chat_request.conversation_id}}
        write_config = {
            "configurable": {
                "thread_id": chat_request.conversation_id,
                "checkpoint_ns": "",
            }
        }
        checkpoint = get_checkpoint()
        existing_state = checkpoint.get(read_config)
        is_new_conversation = not existing_state or not existing_state.get(
            "channel_values", {}
        ).get("messages", [])
        messages = []

        query = chat_request.message
        context = conversation.transcript_id if conversation.transcript_id else ""
        if is_new_conversation:
            new_message = HumanMessage(
                content=query,
                additional_kwargs={"transcript_id": context} if context else {},
            )
            messages.append(new_message)
        else:
            messages = existing_state.get("channel_values", {}).get("messages", [])
            messages.append(
                HumanMessage(
                    content=query,
                    additional_kwargs={"transcript_id": context} if context else {},
                )
            )

        initial_state = ChatBotState(
            messages=messages,
            user_id=user_id,
            conversation_id=chat_request.conversation_id,
            transcript_id=conversation.transcript_id,
        )
        chatbot = initialize_chatbot(checkpoint)

        result = chatbot.invoke(initial_state, config=write_config)
        print(result)
        sent_message_content = result["messages"][-2].content
        sent_message_type = result["messages"][-2].type
        sent_message_id = result["messages"][-2].id
        response_message_content = result["messages"][-1].content
        response_message_type = result["messages"][-1].type
        response_message_id = result["messages"][-1].id

        sent_message = ChatMessageResponse(
            message=sent_message_content,
            type=sent_message_type,
            id=sent_message_id,
        )

        response_message = ChatMessageResponse(
            message=response_message_content,
            type=response_message_type,
            id=response_message_id,
        )

        try:
            texts = [
                sent_message_content if sent_message_type != "tool" else None,
                response_message_content if response_message_type != "tool" else None,
            ]
            metadatas = [
                {
                    "user_id": user_id,
                    "conversation_id": chat_request.conversation_id,
                    "role": sent_message_type,
                },
                {
                    "user_id": user_id,
                    "conversation_id": chat_request.conversation_id,
                    "role": response_message_type,
                },
            ]
            cleaned = [
                (t, m)
                for t, m in zip(texts, metadatas)
                if t is not None and isinstance(t, str)
            ]
            if cleaned:
                messages_vectorstore = get_messages_vectorstore()
                messages_vectorstore.add_texts(
                    [t for t, _ in cleaned], metadatas=[m for _, m in cleaned]
                )
        except Exception as e:
            print(f"Warning: failed to index messages to vector store: {e}")

        return (
            jsonify(
                {
                    "message": "Chat processed successfully",
                    "data": [sent_message.model_dump(), response_message.model_dump()],
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in chat: {e}")
        return jsonify({"message": "An unexpected error occurred"}), 500


def main():
    app.run(port=5000, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
