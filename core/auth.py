"""Account registration and sign-in with bcrypt hashing and basic brute-force lockout."""

import math
import re
import sqlite3
import time

import bcrypt

from core import db

MAX_ATTEMPTS = 5
LOCK_SECONDS = 300
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,30}$")
PUBLIC_FIELDS = "id, username, display_name, country, persona, use_context"


class AuthError(ValueError):
    """An error message that is safe to show to the user."""


def _hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


DUMMY_HASH = _hash("wellsy-timing-guard")


def _matches(password, password_hash):
    return bcrypt.checkpw(password.encode()[:72], password_hash.encode())


def validate_password(password):
    if len(password) < 8:
        raise AuthError("Password must be at least 8 characters.")
    if len(password.encode()) > 72:
        raise AuthError("Password is too long (72 bytes maximum).")


def get_user(user_id):
    return db.one(f"SELECT {PUBLIC_FIELDS} FROM users WHERE id=?", user_id)


def register(username, password):
    username = username.strip()
    if not USERNAME_RE.match(username):
        raise AuthError("Username must be 3-30 characters: letters, numbers or underscores.")
    validate_password(password)
    try:
        user_id = db.insert("users", username=username, password_hash=_hash(password), display_name=username)
    except sqlite3.IntegrityError:
        raise AuthError("That username is already taken.") from None
    return get_user(user_id)


def login(username, password):
    user = db.one("SELECT * FROM users WHERE username=?", username.strip())
    remaining = user["locked_until"] - time.time() if user else 0
    if remaining > 0:
        raise AuthError(f"Too many failed attempts. Try again in {math.ceil(remaining / 60)} min.")
    valid = _matches(password, user["password_hash"] if user else DUMMY_HASH) and user is not None
    if not valid:
        if user:
            attempts = user["failed_attempts"] + 1
            locked = attempts >= MAX_ATTEMPTS
            db.update_user(
                user["id"],
                failed_attempts=0 if locked else attempts,
                locked_until=time.time() + LOCK_SECONDS if locked else 0,
            )
        raise AuthError("Invalid username or password.")
    db.update_user(user["id"], failed_attempts=0)
    return get_user(user["id"])


def verify(user_id, password):
    user = db.one("SELECT password_hash FROM users WHERE id=?", user_id)
    return bool(user) and _matches(password, user["password_hash"])


def change_password(user_id, current, new):
    if not verify(user_id, current):
        raise AuthError("Your current password is incorrect.")
    validate_password(new)
    db.update_user(user_id, password_hash=_hash(new))


def delete_account(user_id, password):
    if not verify(user_id, password):
        raise AuthError("Password is incorrect.")
    db.execute("DELETE FROM users WHERE id=?", user_id)
