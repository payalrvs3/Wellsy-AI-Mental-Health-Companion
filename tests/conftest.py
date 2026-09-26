import pytest

from core import auth, db


@pytest.fixture(autouse=True)
def database(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init()


@pytest.fixture
def user():
    return auth.register("tester", "password123")
