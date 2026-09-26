"""SQLite persistence: versioned migrations and small user-scoped helpers."""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(os.getenv("WELLSY_DB", "data/wellsy.db"))
OWNED = {"chats", "moods", "journal", "thoughts", "assessments"}

MIGRATIONS = [
    """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE COLLATE NOCASE,
        password_hash TEXT NOT NULL,
        display_name TEXT NOT NULL,
        country TEXT,
        persona TEXT NOT NULL DEFAULT 'Wellsy Counselor',
        use_context INTEGER NOT NULL DEFAULT 1,
        failed_attempts INTEGER NOT NULL DEFAULT 0,
        locked_until REAL NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE chats (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        title TEXT NOT NULL DEFAULT 'New chat',
        persona TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY,
        chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
        role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
        content TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE moods (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        score INTEGER NOT NULL CHECK (score BETWEEN 1 AND 5),
        emotions TEXT NOT NULL DEFAULT '',
        activities TEXT NOT NULL DEFAULT '',
        sleep_hours REAL,
        note TEXT NOT NULL DEFAULT '',
        logged_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE journal (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        tags TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE thoughts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        situation TEXT NOT NULL DEFAULT '',
        thought TEXT NOT NULL,
        emotion TEXT NOT NULL DEFAULT '',
        traps TEXT NOT NULL DEFAULT '',
        evidence_for TEXT NOT NULL DEFAULT '',
        evidence_against TEXT NOT NULL DEFAULT '',
        balanced TEXT NOT NULL DEFAULT '',
        intensity_before INTEGER NOT NULL,
        intensity_after INTEGER NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE assessments (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        kind TEXT NOT NULL,
        score INTEGER NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE safety_plans (
        user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
        data TEXT NOT NULL,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX idx_chats_user ON chats(user_id, updated_at);
    CREATE INDEX idx_messages_chat ON messages(chat_id, id);
    CREATE INDEX idx_moods_user ON moods(user_id, logged_at);
    CREATE INDEX idx_journal_user ON journal(user_id, created_at);
    """,
]


@contextmanager
def conn():
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init():
    """Create the database and apply any pending migrations."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with conn() as con:
        con.execute("PRAGMA journal_mode=WAL")
        version = con.execute("PRAGMA user_version").fetchone()[0]
        for number, script in enumerate(MIGRATIONS[version:], start=version + 1):
            con.executescript(script)
            con.execute(f"PRAGMA user_version={number}")


def query(sql, *args):
    with conn() as con:
        return [dict(row) for row in con.execute(sql, args)]


def one(sql, *args):
    found = query(sql, *args)
    return found[0] if found else None


def execute(sql, *args):
    with conn() as con:
        return con.execute(sql, args).lastrowid


def _assignments(fields):
    return ", ".join(f"{name}=?" for name in fields)


def insert(table, **values):
    assert table in OWNED | {"users"}
    marks = ", ".join("?" * len(values))
    return execute(f"INSERT INTO {table} ({', '.join(values)}) VALUES ({marks})", *values.values())


def update(table, row_id, user_id, **fields):
    assert table in OWNED
    execute(f"UPDATE {table} SET {_assignments(fields)} WHERE id=? AND user_id=?", *fields.values(), row_id, user_id)


def delete(table, row_id, user_id):
    assert table in OWNED
    execute(f"DELETE FROM {table} WHERE id=? AND user_id=?", row_id, user_id)


def update_user(user_id, **fields):
    execute(f"UPDATE users SET {_assignments(fields)} WHERE id=?", *fields.values(), user_id)


def rows(table, user_id, where="", args=(), order="id DESC", limit=None):
    """Select a user's rows. `where` and `order` are developer-supplied SQL, never user input."""
    assert table in OWNED
    sql = f"SELECT * FROM {table} WHERE user_id=?" + (f" AND ({where})" if where else "")
    sql += f" ORDER BY {order}" + (f" LIMIT {int(limit)}" if limit else "")
    return query(sql, user_id, *args)


def messages(user_id, chat_id):
    return query(
        "SELECT m.role, m.content, m.created_at FROM messages m JOIN chats c ON c.id = m.chat_id "
        "WHERE c.id=? AND c.user_id=? ORDER BY m.id",
        chat_id,
        user_id,
    )


def add_message(user_id, chat_id, role, content):
    with conn() as con:
        con.execute(
            "INSERT INTO messages (chat_id, role, content) SELECT id, ?, ? FROM chats WHERE id=? AND user_id=?",
            (role, content, chat_id, user_id),
        )
        con.execute("UPDATE chats SET updated_at=CURRENT_TIMESTAMP WHERE id=?", (chat_id,))


def get_plan(user_id):
    found = one("SELECT data FROM safety_plans WHERE user_id=?", user_id)
    return json.loads(found["data"]) if found else {}


def save_plan(user_id, plan):
    execute(
        "INSERT INTO safety_plans (user_id, data) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE "
        "SET data=excluded.data, updated_at=CURRENT_TIMESTAMP",
        user_id,
        json.dumps(plan),
    )


def export_all(user_id):
    """Everything stored for a user, for the data-download feature."""
    data = {table: rows(table, user_id) for table in ("moods", "journal", "thoughts", "assessments")}
    data["chats"] = [{**chat, "messages": messages(user_id, chat["id"])} for chat in rows("chats", user_id)]
    data["safety_plan"] = get_plan(user_id)
    return data
