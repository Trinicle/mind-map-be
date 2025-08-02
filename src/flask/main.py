import os
from flask import Flask, request, jsonify
from gotrue import Session
from src.agent.main import analyze_transcript
from src.flask.models.mindmap_models import MindMapResponse
from src.flask.supabase.auth import UserModel, refresh_session, signin, signout, signup
from flask_cors import CORS
from gotrue.errors import AuthApiError
from gotrue.types import AuthResponse

from src.flask.supabase.content import insert_content
from src.flask.supabase.mindmap import (
    get_mindmap_detail,
    get_user_mindmaps,
    get_user_mindmaps_by_query,
    insert_mindmap,
)
from src.flask.supabase.tag import get_tags, insert_tags
from src.flask.supabase.topic import insert_topic
import json
from datetime import datetime

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


@app.route("/auth/session", methods=["GET"])
def handle_session():
    try:
        session = refresh_session(request)
        return jsonify({"message": "Session found", "data": session}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/dashboard/mindmap", methods=["GET"])
def handle_mindmap_get():
    try:
        cards = get_user_mindmaps(request)
        return jsonify({"message": "Mindmap cards found", "data": cards}), 200
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
        return jsonify({"message": "Mindmap cards found", "data": cards}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/dashboard/mindmap/<mindmap_id>", methods=["GET"])
def handle_mindmap_detail(mindmap_id: str):
    try:
        mindmap = get_mindmap_detail(request, mindmap_id)
        return jsonify({"message": "Mindmap detail found", "data": mindmap}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


@app.route("/dashboard/mindmap/tags", methods=["GET"])
def handle_mindmap_tags():
    try:
        tags = get_tags(request)
        return jsonify({"message": "Mindmap tags found", "data": tags}), 200
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

        # Convert to absolute path for the agent
        absolute_file_path = os.path.abspath(file_path)

        auth_token = request.headers.get("Authorization")
        if not auth_token:
            return jsonify({"message": "Authorization token is required"}), 401

        auth_token = auth_token.replace("Bearer ", "")

        # Analyze transcript using AI agent
        analysis_result = analyze_transcript(
            title,
            description,
            date,
            absolute_file_path,
            auth_token,
        )
        if analysis_result is None:
            os.remove(file_path)
            return jsonify({"message": "Failed to analyze transcript"}), 400

        # Clean up uploaded file
        os.remove(file_path)

        # Extract data from analysis
        transcript_id = analysis_result.get("transcript_id", "")
        participants = analysis_result.get("participants", [])
        topics_data = analysis_result.get("topics", [])

        # Insert mindmap into database
        mindmap = insert_mindmap(
            request, title, description, date, participants, transcript_id
        )
        if mindmap is None:
            return jsonify({"message": "Failed to create mindmap"}), 400
        print("inserted mindmap")

        # Insert tags
        tags = insert_tags(request, tags, mindmap["id"])

        # Insert topics and their content
        for topic_data in topics_data:
            topic = insert_topic(request, topic_data["title"], mindmap["id"])
            print("inserted topic")
            if topic is None:
                continue

            for content_item in topic_data.get("content", []):
                if content_item and content_item.get("text"):
                    insert_content(
                        request,
                        content_item["text"],
                        content_item["speaker"],
                        topic["id"],
                    )
                    print("inserted content")

        response: MindMapResponse = {
            "id": mindmap["id"],
            "title": mindmap["title"],
            "description": mindmap["description"],
            "date": mindmap["date"],
            "tags": [tag["name"] for tag in tags],
        }

        return jsonify({"message": "Mindmap created", "data": response}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


def main():
    app.run(port=5000, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
