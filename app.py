from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import time
import json
import os
import logging

app = Flask(__name__)

print("🔥 RUNNING THIS FILE")

# -------------------------
# CORS
# -------------------------
CORS(app, resources={r"/*": {"origins": "*"}})

# -------------------------
# ENABLE FLASK DEBUG LOGGING (IMPORTANT)
# -------------------------
logging.basicConfig(level=logging.INFO)
werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.INFO)

# -------------------------
# DB SETUP
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "logs.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            user_agent TEXT,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()

# -------------------------
# GLOBAL REQUEST LOGGER (🔥 THIS IS THE IMPORTANT PART)
# -------------------------
@app.before_request
def log_every_request():
    print("\n================ NEW REQUEST ================")
    print("Method:", request.method)
    print("Path:", request.path)
    print("IP:", request.remote_addr)
    print("User-Agent:", request.headers.get("User-Agent"))
    print("Headers:", dict(request.headers))


# -------------------------
# GET CLIENT IP (safe behind proxies)
# -------------------------
def get_ip():
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr


# -------------------------
# ROUTES
# -------------------------
@app.route("/")
def home():
    return "Backend is running ✅"


@app.route("/track", methods=["GET"])
def track():
    ip = get_ip()
    ua = request.headers.get("User-Agent", "")
    now = time.strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "ip": ip,
        "user_agent": ua,
        "time": now
    }

    # TERMINAL LOG
    print("\n🔥 NEW VISITOR TRACKED:")
    print(json.dumps(data, indent=2))

    # SAVE TO DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO logs (ip, user_agent, time) VALUES (?, ?, ?)",
        (ip, ua, now)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "status": "logged",
        "ip": ip,
        "user_agent": ua,
        "time": now
    })


@app.route("/logs", methods=["GET"])
def logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ip, user_agent, time FROM logs ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    return jsonify([
        {"ip": r[0], "user_agent": r[1], "time": r[2]}
        for r in rows
    ])


# -------------------------
# RUN SERVER
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
        use_reloader=False  # prevents double logs in terminal
    )