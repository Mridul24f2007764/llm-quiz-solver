from flask import Flask, request, jsonify
import threading
from solver import solve_quiz
import os

app = Flask(__name__)

EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")

@app.route("/", methods=["POST"])
def handle_quiz():
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON payload"}), 400

    email = data.get("email")
    secret = data.get("secret")
    url = data.get("url")

    if not (email and secret and url):
        return jsonify({"error": "Missing required fields"}), 400

    if secret != SECRET:
        return jsonify({"error": "Invalid secret"}), 403

    # Run the solver asynchronously to meet 3-minute window
    threading.Thread(target=solve_quiz, args=(email, secret, url)).start()
    return jsonify({"message": "Accepted, solving started"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
