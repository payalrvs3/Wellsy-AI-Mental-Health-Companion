import sqlite3

import pytest

from core import auth, db


def other_user():
    return auth.register("second", "password123")


def test_init_is_idempotent():
    db.init()
    assert db.one("PRAGMA user_version")["user_version"] == len(db.MIGRATIONS)


def test_rows_are_scoped_to_their_owner(user):
    mood = db.insert("moods", user_id=user["id"], score=4)
    stranger = other_user()
    assert db.rows("moods", stranger["id"]) == []
    db.delete("moods", mood, stranger["id"])
    assert len(db.rows("moods", user["id"])) == 1


def test_update_ignores_other_users(user):
    entry = db.insert("journal", user_id=user["id"], title="mine", body="text")
    db.update("journal", entry, other_user()["id"], title="changed")
    assert db.rows("journal", user["id"])[0]["title"] == "mine"


def test_messages_are_owner_checked(user):
    chat = db.insert("chats", user_id=user["id"], persona="Wellsy Counselor")
    stranger = other_user()
    db.add_message(stranger["id"], chat, "user", "intruder")
    db.add_message(user["id"], chat, "user", "hello")
    assert [m["content"] for m in db.messages(user["id"], chat)] == ["hello"]
    assert db.messages(stranger["id"], chat) == []


def test_deleting_a_chat_removes_its_messages(user):
    chat = db.insert("chats", user_id=user["id"], persona="Wellsy Counselor")
    db.add_message(user["id"], chat, "user", "hello")
    db.delete("chats", chat, user["id"])
    assert db.query("SELECT * FROM messages") == []


def test_deleting_an_account_removes_everything(user):
    uid = user["id"]
    chat = db.insert("chats", user_id=uid, persona="Wellsy Counselor")
    db.add_message(uid, chat, "user", "hello")
    db.insert("moods", user_id=uid, score=3)
    db.insert("journal", user_id=uid, title="t", body="b")
    db.insert("thoughts", user_id=uid, thought="t", intensity_before=1, intensity_after=1)
    db.insert("assessments", user_id=uid, kind="GAD-7", score=3)
    db.save_plan(uid, {"coping": "walk"})
    auth.delete_account(uid, "password123")
    for table in ("users", "chats", "messages", "moods", "journal", "thoughts", "assessments", "safety_plans"):
        assert db.query(f"SELECT * FROM {table}") == [], table


def test_mood_score_is_validated(user):
    with pytest.raises(sqlite3.IntegrityError):
        db.insert("moods", user_id=user["id"], score=9)


def test_safety_plan_roundtrip_and_export(user):
    uid = user["id"]
    assert db.get_plan(uid) == {}
    db.save_plan(uid, {"coping": "walk"})
    db.save_plan(uid, {"coping": "call a friend"})
    export = db.export_all(uid)
    assert export["safety_plan"] == {"coping": "call a friend"}
    assert set(export) == {"moods", "journal", "thoughts", "assessments", "chats", "safety_plan"}
