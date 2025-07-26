from flask import Flask, request, jsonify, make_response

app = Flask(__name__)


@app.route("/api/authenticate", methods=["POST"])
def authenticate():
    data = request.json
    return jsonify({"message": "Authenticated"}), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True, use_reloader=False)
