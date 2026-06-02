from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.app import app
from src.services.db import init_db
from src.services.registration_service import reset_submission_locks


@pytest.fixture()
def client(tmp_path: Path):
    db_path = tmp_path / "integration_app.db"
    init_db(db_path)
    reset_submission_locks()

    app.config["TESTING"] = True
    app.config["REGISTRATION_DB_PATH"] = str(db_path)

    with app.test_client() as flask_client:
        yield flask_client, db_path


def _extract_submission_token(response_body: bytes) -> str:
    marker = b'name="submission_token" value="'
    start = response_body.find(marker)
    assert start != -1
    start += len(marker)
    end = response_body.find(b'"', start)
    return response_body[start:end].decode("utf-8")


def test_register_page_is_available_for_signed_out_user(client) -> None:
    flask_client, _ = client
    response = flask_client.get("/register")
    assert response.status_code == 200
    assert b"Create account" in response.data


def test_successful_registration_redirects_to_home(client) -> None:
    flask_client, db_path = client
    page = flask_client.get("/register")
    token = _extract_submission_token(page.data)

    response = flask_client.post(
        "/register",
        data={"email": "success@example.com", "password": "abc12345", "submission_token": token},
        follow_redirects=False,
    )

    assert response.status_code in {302, 303}
    assert "/?registered=1" in response.headers["Location"]

    with sqlite3.connect(db_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM user_accounts WHERE email = ?",
            ("success@example.com",),
        ).fetchone()[0]
    assert count == 1


def test_registration_rejects_invalid_password(client) -> None:
    flask_client, db_path = client
    page = flask_client.get("/register")
    token = _extract_submission_token(page.data)

    response = flask_client.post(
        "/register",
        data={"email": "badpass@example.com", "password": "abcdefg", "submission_token": token},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Password must be at least 8 characters" in response.data

    with sqlite3.connect(db_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM user_accounts WHERE email = ?",
            ("badpass@example.com",),
        ).fetchone()[0]
    assert count == 0


def test_registration_rejects_duplicate_email(client) -> None:
    flask_client, db_path = client
    token_1 = _extract_submission_token(flask_client.get("/register").data)
    flask_client.post(
        "/register",
        data={"email": "duplicate@example.com", "password": "abc12345", "submission_token": token_1},
    )

    token_2 = _extract_submission_token(flask_client.get("/register").data)
    response = flask_client.post(
        "/register",
        data={"email": "duplicate@example.com", "password": "abc12345", "submission_token": token_2},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"already registered" in response.data

    with sqlite3.connect(db_path) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM user_accounts WHERE email = ?",
            ("duplicate@example.com",),
        ).fetchone()[0]
    assert count == 1


def test_registration_rejects_whitespace_email(client) -> None:
    flask_client, _ = client
    token = _extract_submission_token(flask_client.get("/register").data)

    response = flask_client.post(
        "/register",
        data={"email": " user@example.com ", "password": "abc12345", "submission_token": token},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"must not contain leading or trailing whitespace" in response.data


def test_registration_accessible_when_signed_in(client) -> None:
    flask_client, _ = client

    with flask_client.session_transaction() as session_data:
        session_data["user_id"] = "existing-user"

    response = flask_client.get("/register")
    assert response.status_code == 200
    assert b"Create account" in response.data
