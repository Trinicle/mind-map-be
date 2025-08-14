import os
from flask import Flask, request, jsonify
from gotrue import Session
from langchain_openai import ChatOpenAI
from langchain_redis import RedisChatMessageHistory
from src.agent.graph import transcript_graph
from src.agent.state import TranscriptState, ChatBotState
from src.agent.chatbot import create_rag_agent
from src.agent.connection import (
    get_checkpoint,
    get_redis_client,
    get_vectorstore_context,
)
from langchain_core.messages import HumanMessage
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
from src.flask.supabase.mindmap import (
    get_mindmap_detail,
    get_user_mindmaps,
    get_user_mindmaps_by_query,
)
from src.flask.supabase.question import get_questions
from src.flask.supabase.tag import get_tags
from src.flask.supabase.topic import (
    get_topic_detail,
    get_topics,
)
import json
from datetime import datetime

from src.flask.supabase.transcript import (
    get_transcript,
)
from src.agent.connection import get_messages_vectorstore
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
from src.flask.supabase.utils import (
    insert_transcript_data_async,
    load_conversation_history,
)

UPLOAD_FOLDER = "uploads"

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, max_completion_tokens=500)
app = Flask(__name__)
CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:4200"],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "PUT", "POST", "DELETE", "OPTIONS"],
)


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
        request_tags = request.args.getlist("tags")
        request_title = request.args.get("title")
        request_date = request.args.get("date")
        date = (
            datetime.fromisoformat(request_date.replace("Z", "+00:00"))
            if request_date
            else None
        )
        cards = get_user_mindmaps_by_query(request, request_title, request_tags, date)
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
        serialized_tags = [tag.model_dump() for tag in tags]
        return jsonify({"message": "Mindmap tags found", "data": serialized_tags}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/dashboard/mindmap", methods=["POST"])
async def handle_mindmap_create():
    try:
        file = request.files.get("file")
        if not file:
            return jsonify({"message": "File is required"}), 400

        file_bytes = file.read()
        title = request.form.get("title")
        description = request.form.get("description")
        date = request.form.get("date")
        tags = json.loads(request.form.get("tags", "[]"))

        transcript_state = TranscriptState(
            file=file_bytes,
            file_name=file.filename,
        )

        result_dict = await transcript_graph.ainvoke(transcript_state)

        result = TranscriptState(**result_dict)

        mindmap = await insert_transcript_data_async(
            request, result, title, description, date, tags
        )

        return (
            jsonify({"message": "Mindmap created", "data": mindmap.model_dump()}),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/mindmap/<mindmap_id>", methods=["GET"])
def handle_mindmap_get_detail(mindmap_id: str):
    try:
        mindmap = get_mindmap_detail(request, mindmap_id)
        return (
            jsonify({"message": "Mindmap detail found", "data": mindmap.model_dump()}),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/mindmap/<mindmap_id>/topics", methods=["GET"])
def handle_mindmap_topics(mindmap_id: str):
    try:
        topics = get_topics(request, mindmap_id)
        return (
            jsonify(
                {
                    "message": "Mindmap topics found",
                    "data": [topic.model_dump() for topic in topics],
                }
            ),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/mindmap/<mindmap_id>/transcript", methods=["GET"])
def handle_transcript_get_detail(mindmap_id: str):
    try:
        transcript = get_transcript(request, mindmap_id)
        return (
            jsonify(
                {
                    "message": "Transcript detail found",
                    "data": transcript.model_dump(),
                }
            ),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/topic/<topic_id>", methods=["GET"])
def handle_topic_get_detail(topic_id: str):
    try:
        topic = get_topic_detail(request, topic_id)
        return (
            jsonify({"message": "Topic detail found", "data": topic.model_dump()}),
            200,
        )
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/mindmap/<mindmap_id>/questions", methods=["GET"])
def handle_mindmap_questions(mindmap_id: str):
    try:
        questions = get_questions(request, mindmap_id)
        return (
            jsonify(
                {
                    "message": "Topic questions found",
                    "data": [question.model_dump() for question in questions],
                }
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

        conversation = create_conversation(
            request, conversation_request.query, conversation_request.transcript_id
        )

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


@app.route("/conversations/<conversation_id>", methods=["GET"])
async def handle_get_conversation(conversation_id: str):
    """Get conversation history (last 10 messages) and load into Redis"""
    try:
        history = await load_conversation_history(conversation_id)

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

        write_config = {
            "configurable": {
                "thread_id": chat_request.conversation_id,
                "checkpoint_ns": "",
            }
        }

        context = conversation.transcript_id if conversation.transcript_id else ""
        messages = [
            HumanMessage(
                content=chat_request.message,
                additional_kwargs={"transcript_id": context} if context else {},
            )
        ]

        with get_checkpoint() as checkpoint, get_vectorstore_context() as vectorstore:
            initial_state = ChatBotState(
                messages=messages,
            )
            chatbot = create_rag_agent(
                checkpoint, llm, vectorstore, user_id, chat_request.conversation_id
            )
            result = chatbot.invoke(initial_state, config=write_config)

        messages = result["messages"]

        human_message = None
        ai_message = None

        for msg in reversed(messages):
            if msg.type == "human" and human_message is None:
                human_message = msg
            elif msg.type == "ai" and ai_message is None:
                ai_message = msg

            if human_message and ai_message:
                break

        sent_message = ChatMessageResponse(
            message=human_message.content,
            type=human_message.type,
            id=human_message.id,
        )

        response_message = ChatMessageResponse(
            message=ai_message.content,
            type=ai_message.type,
            id=ai_message.id,
        )

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
