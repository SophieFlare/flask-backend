from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import time
import json
import os
app = Flask(__name__)
print("🔥 RUNNING THIS FILE")
# ✅ PRODUCTION CORS FIX (IMPORTANT)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/")
def home():
    return "Backend is running ✅"
# -------------------------
# DB SETUP
# -------------------------
def init_db():
    conn = sqlite3.connect("logs.db")
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
# GET CLIENT IP
# -------------------------
def get_ip():
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr


# -------------------------
# TRACK ROUTE
# -------------------------
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

    # ✅ TERMINAL LOG
    print("\n🔥 NEW VISITOR:")
    print(json.dumps(data, indent=2))

    # ✅ SAVE TO DB
    conn = sqlite3.connect("logs.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO logs (ip, user_agent, time) VALUES (?, ?, ?)",
        (ip, ua, now)
    )
    conn.commit()
    conn.close()

    return jsonify({"status": "logged"})


# -------------------------
# GET LOGS
# -------------------------
@app.route("/logs", methods=["GET"])
def logs():

    conn = sqlite3.connect("logs.db")
    c = conn.cursor()
    c.execute("SELECT ip, user_agent, time FROM logs ORDER BY id DESC")

    rows = c.fetchall()
    conn.close()

    return jsonify([
        {"ip": r[0], "user_agent": r[1], "time": r[2]}
        for r in rows
    ])


# -------------------------
# RENDER ENTRY POINT (IMPORTANT)
# -------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)