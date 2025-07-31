import os
from flask import Flask, Request, request, jsonify
from gotrue import Session
from src.agent.main import create_mindmap
from src.flask.models.mindmap_models import MindMapPostRequest, MindMapResponse
from src.flask.supabase.auth import UserModel, get_session, signin, signout, signup
from flask_cors import CORS
from gotrue.errors import AuthApiError
from gotrue.types import AuthResponse

from src.flask.supabase.content import insert_content
from src.flask.supabase.mindmap import (
    get_mindmap_detail,
    get_tags,
    get_user_mindmaps,
    get_user_mindmaps_by_query,
    insert_mindmap,
)
from src.flask.supabase.tags import insert_tags
from src.flask.supabase.topic import insert_topic
import json
from datetime import datetime

UPLOAD_FOLDER = "uploads"

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

        mindmap_request: MindMapPostRequest = {
            "title": title,
            "description": description,
            "date": date,
            "file_path": file_path,
        }

        mindmap_agent_output = create_mindmap(mindmap_request)
        if mindmap_agent_output is None:
            return jsonify({"message": "Failed to create mindmap"}), 400

        os.remove(file_path)

        mindmap = insert_mindmap(
            request,
            title,
            description,
            date,
            mindmap_agent_output["participants"],
        )
        print("inserted mindmap")

        tags = insert_tags(request, tags)

        for output_topic in mindmap_agent_output["topics"]:
            topic = insert_topic(request, output_topic["title"], mindmap["id"])
            print("inserted topic")
            if topic is None:
                continue

            for content in output_topic["content"]:
                if content is None:
                    continue
                insert_content(request, content["text"], topic["id"])
                print("inserted content")

        response: MindMapResponse = {
            "id": mindmap["id"],
            "title": mindmap["title"],
            "description": mindmap["description"],
            "date": mindmap["date"],
            "tags": tags,
        }

        return jsonify({"message": "Mindmap created", "data": response}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred"}), 500


def main():
    app.run(port=5000, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
