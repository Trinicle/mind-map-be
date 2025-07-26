from flask import Flask, request, jsonify, make_response
from src.supabase.supabase import UserModel
from src.supabase.supabase import signup
from flask_cors import CORS
from gotrue.errors import AuthApiError

app = Flask(__name__)
CORS(app, supports_credentials=True)


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:4200")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response


@app.route("/auth/signup", methods=["POST"])
def handle_signup():
    try:
        data: UserModel = request.json
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        signup(data)
        return jsonify({"message": "Authenticated"}), 200
    except AuthApiError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred"}), 500


def main():
    app.run(port=5000, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
