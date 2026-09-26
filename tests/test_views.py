from pathlib import Path

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from core import ai, auth, db
from scripts.seed_demo import seed

ROOT = Path(__file__).resolve().parents[1]
VIEWS = ["home", "chat", "mood", "journal", "insights", "assessments", "toolkit", "support", "settings"]


@pytest.fixture(autouse=True)
def no_navigation(monkeypatch):
    """Views are run on their own here, so page links have no navigation to resolve against."""
    monkeypatch.setattr(st, "page_link", lambda *args, **kwargs: None)


def open_view(name, user):
    app = AppTest.from_file(str(ROOT / "views" / f"{name}.py"), default_timeout=30)
    app.session_state["user"] = user
    return app.run()


def shows_crisis_card(app):
    return any("not alone" in item.value for item in app.markdown)


@pytest.mark.parametrize("name", VIEWS)
def test_pages_render_for_a_new_user(name, user):
    assert not open_view(name, user).exception


@pytest.mark.parametrize("name", VIEWS)
def test_pages_render_with_data(name):
    seed()
    assert not open_view(name, auth.login("demo", "demo-password")).exception


def test_mood_check_in_is_saved(user):
    app = open_view("mood", user)
    app.select_slider[0].set_value(5)
    app.button[0].click().run()
    assert [m["score"] for m in db.rows("moods", user["id"])] == [5]


def test_journal_saves_entries_and_rejects_empty_ones(user):
    app = open_view("journal", user)
    app.button[0].click().run()
    assert app.warning and not db.rows("journal", user["id"])
    app.text_area[0].input("I felt calm today").run()
    app.button[0].click().run()
    assert db.rows("journal", user["id"])[0]["body"] == "I felt calm today"


def test_chat_saves_the_exchange_and_titles_the_chat(user, monkeypatch):
    monkeypatch.setattr(ai, "stream_reply", lambda *args, **kwargs: iter(["Hello ", "there"]))
    app = open_view("chat", user)
    app.chat_input[0].set_value("I feel overwhelmed at work today, honestly").run()
    chat = db.rows("chats", user["id"])[0]
    assert chat["title"] == "I feel overwhelmed at work today, honest"
    assert [(m["role"], m["content"]) for m in db.messages(user["id"], chat["id"])][1] == ("assistant", "Hello there")
    assert not shows_crisis_card(app)


def test_chat_sends_combined_context_when_enabled(user, monkeypatch):
    calls = []

    def fake(history, persona, country=None, context="", risk=False):
        calls.append(context)
        return iter(["ok"])

    monkeypatch.setattr(ai, "stream_reply", fake)
    db.insert("moods", user_id=user["id"], score=4)
    db.insert("assessments", user_id=user["id"], kind="GAD-7", score=3)
    db.insert("journal", user_id=user["id"], title="t", body="b", tags="calm")
    open_view("chat", user).chat_input[0].set_value("hello").run()
    assert "mood —" in calls[0] and "check-ins — GAD-7 3" in calls[0] and "journal —" in calls[0] and "calm" in calls[0]


def test_chat_sends_no_context_when_personalisation_is_off(user, monkeypatch):
    calls = []

    def fake(history, persona, country=None, context="", risk=False):
        calls.append(context)
        return iter(["ok"])

    monkeypatch.setattr(ai, "stream_reply", fake)
    db.update_user(user["id"], use_context=0)
    db.insert("moods", user_id=user["id"], score=4)
    open_view("chat", auth.get_user(user["id"])).chat_input[0].set_value("hello").run()
    assert calls[0] == ""


def test_chat_shows_support_when_risk_language_appears(user, monkeypatch):
    monkeypatch.setattr(ai, "stream_reply", lambda *args, **kwargs: iter(["I'm here with you."]))
    app = open_view("chat", user)
    app.chat_input[0].set_value("I want to die").run()
    assert shows_crisis_card(app)


def test_chat_shows_a_friendly_error_when_the_ai_fails(user, monkeypatch):
    def failing(*args, **kwargs):
        raise ai.AIError("Wellsy is busy right now.")
        yield

    monkeypatch.setattr(ai, "stream_reply", failing)
    app = open_view("chat", user)
    app.chat_input[0].set_value("hello").run()
    assert app.error[0].value == "Wellsy is busy right now."
    assert [m["role"] for m in db.messages(user["id"], db.rows("chats", user["id"])[0]["id"])] == ["user"]


def test_assessment_is_scored_and_flags_item_nine(user):
    app = open_view("assessments", user)
    app.button[0].click().run()
    assert app.warning and not db.rows("assessments", user["id"])
    for number in range(1, 10):
        app.radio(key=f"PHQ-9_{number}").set_value(2 if number == 9 else 1)
    app.button[0].click().run()
    assert db.rows("assessments", user["id"])[0]["score"] == 10
    assert shows_crisis_card(app)


def test_thought_record_can_be_suggested_and_saved(user, monkeypatch):
    monkeypatch.setattr(ai, "complete", lambda prompt: "Try this balanced thought.")
    app = open_view("toolkit", user)
    app.text_area[1].input("I always fail").run()
    app.button[0].click().run()
    assert app.info[0].value == "Try this balanced thought."
    app.button[1].click().run()
    assert db.rows("thoughts", user["id"])[0]["thought"] == "I always fail"


def test_settings_are_saved(user):
    app = open_view("settings", user)
    app.text_input[0].set_value("Sam")
    app.selectbox[0].select("India")
    app.button[0].click().run()
    saved = auth.get_user(user["id"])
    assert (saved["display_name"], saved["country"]) == ("Sam", "India")


def test_safety_plan_is_saved(user):
    app = open_view("support", user)
    app.text_area[0].input("Feeling numb").run()
    app.button[0].click().run()
    assert db.get_plan(user["id"])["warning_signs"] == "Feeling numb"


def test_sign_up_then_bad_sign_in():
    app = AppTest.from_file(str(ROOT / "views" / "login.py"), default_timeout=30).run()
    app.text_input[2].set_value("newuser")
    app.text_input[3].set_value("password123")
    app.text_input[4].set_value("different")
    app.button[1].click().run()
    assert "do not match" in app.error[0].value
    app.text_input[4].set_value("password123")
    app.button[1].click().run()
    assert app.session_state["user"]["username"] == "newuser"
    fresh = AppTest.from_file(str(ROOT / "views" / "login.py"), default_timeout=30).run()
    fresh.text_input[0].set_value("newuser")
    fresh.text_input[1].set_value("wrong-password")
    fresh.button[0].click().run()
    assert fresh.error[0].value == "Invalid username or password."
