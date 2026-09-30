import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# На Railway база лежит в томе /data, локально рядом с проектом
DB_PATH = os.environ.get(
    "DB_PATH",
    "/data/messages.db" if os.path.isdir("/data") else "messages.db",
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )


init_db()


@app.route("/")
def index():
    with get_db() as conn:
        messages = conn.execute(
            "SELECT name, text, created_at FROM messages ORDER BY id DESC LIMIT 200"
        ).fetchall()
    return render_template("index.html", messages=messages)


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()[:30] or "Аноним"
    text = request.form.get("text", "").strip()[:300]
    if text:
        with get_db() as conn:
            conn.execute(
                "INSERT INTO messages (name, text) VALUES (?, ?)", (name, text)
            )
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)