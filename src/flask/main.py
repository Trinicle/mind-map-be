from flask import Flask, request, jsonify, make_response
from src.flask.supabase.auth import UserModel, login, signup
from flask_cors import CORS
from gotrue.errors import AuthApiError
from gotrue.types import AuthResponse

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:4200")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response


def serialize_auth_response(response: AuthResponse):
    return {
        "user": response.user.model_dump(mode="json"),
        "session": response.session.model_dump(mode="json"),
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


@app.route("/auth/login", methods=["POST"])
def handle_login():
    try:
        data: UserModel = request.json
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400
        response = login(email, password)
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


def main():
    app.run(port=5000, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
