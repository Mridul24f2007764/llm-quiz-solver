# server.py
import os
import time
import threading
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from solver import start_solve_background

load_dotenv()
SECRET = os.getenv("SECRET")
EMAIL = os.getenv("EMAIL")
PORT = int(os.getenv("PORT", 5000))

app = Flask(__name__)

def bad_request():
    return jsonify({"error": "Invalid JSON payload"}), 400

@app.route("/", methods=["POST"])
def receive():
    try:
        payload = request.get_json(force=True)
    except Exception:
        return bad_request()

    if not payload:
        return bad_request()

    email = payload.get("email")
    secret = payload.get("secret")
    url = payload.get("url")

    if not (email and secret and url):
        return bad_request()

    if secret != SECRET:
        return jsonify({"error": "Invalid secret"}), 403

    # Immediately return 200
    resp = jsonify({"message": "Accepted, solving started"})
    # start background thread to solve (non-blocking)
    t = threading.Thread(target=start_solve_background, args=(email, secret, url), daemon=True)
    t.start()
    return resp, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
