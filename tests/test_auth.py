import time

import pytest

from core import auth


def test_register_and_login_are_case_insensitive(user):
    assert user["username"] == "tester"
    assert "password_hash" not in user
    assert auth.login("TESTER", "password123")["id"] == user["id"]


@pytest.mark.parametrize("name", ["ab", "has space", "bad!", "x" * 31])
def test_invalid_usernames_are_rejected(name):
    with pytest.raises(auth.AuthError):
        auth.register(name, "password123")


def test_duplicate_usernames_are_rejected(user):
    with pytest.raises(auth.AuthError, match="taken"):
        auth.register("TESTER", "password123")


@pytest.mark.parametrize("password", ["short", "x" * 73])
def test_password_rules(password):
    with pytest.raises(auth.AuthError):
        auth.register("someone", password)


def test_unknown_user_and_wrong_password_look_the_same(user):
    messages = set()
    for name, password in [("tester", "wrong-password"), ("nobody", "password123")]:
        with pytest.raises(auth.AuthError) as error:
            auth.login(name, password)
        messages.add(str(error.value))
    assert messages == {"Invalid username or password."}


def test_lockout_after_repeated_failures_then_recovery(user, monkeypatch):
    for _ in range(auth.MAX_ATTEMPTS):
        with pytest.raises(auth.AuthError, match="Invalid"):
            auth.login("tester", "nope")
    with pytest.raises(auth.AuthError, match="Too many"):
        auth.login("tester", "password123")
    later = time.time() + auth.LOCK_SECONDS + 1
    monkeypatch.setattr(auth.time, "time", lambda: later)
    assert auth.login("tester", "password123")["id"] == user["id"]


def test_change_password(user):
    with pytest.raises(auth.AuthError):
        auth.change_password(user["id"], "wrong", "newpassword1")
    auth.change_password(user["id"], "password123", "newpassword1")
    assert auth.login("tester", "newpassword1")
    with pytest.raises(auth.AuthError):
        auth.login("tester", "password123")


def test_delete_account_requires_the_password(user):
    with pytest.raises(auth.AuthError):
        auth.delete_account(user["id"], "wrong")
    auth.delete_account(user["id"], "password123")
    assert auth.get_user(user["id"]) is None
