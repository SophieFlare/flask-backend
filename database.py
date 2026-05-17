import sqlite3
import os

DB_NAME = "logs.db"


# -----------------------------
# INIT DATABASE
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            user_agent TEXT,
            time TEXT
        )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# SAVE LOG
# -----------------------------
def save_log(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs (ip, user_agent, time)
        VALUES (?, ?, ?)
    """, (
        data.get("ip"),
        data.get("user_agent"),
        data.get("time")
    ))

    conn.commit()
    conn.close()


# -----------------------------
# GET ALL LOGS
# -----------------------------
def get_logs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ip, user_agent, time
        FROM logs
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "ip": r[0],
            "user_agent": r[1],
            "time": r[2]
        }
        for r in rows
    ]