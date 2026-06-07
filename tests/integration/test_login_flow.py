from __future__ import annotations

from pathlib import Path

import pytest

from src.app import app
from src.services.auth_service import reset_auth_tracking
from src.services.db import get_connection, init_db
from src.services.registration_service import create_user_account


@pytest.fixture()
def client(tmp_path: Path):
    db_path = tmp_path / "login_integration.db"
    init_db(db_path)
    reset_auth_tracking()

    app.config["TESTING"] = True
    app.config["AUTH_DB_PATH"] = str(db_path)
    app.config["REGISTRATION_DB_PATH"] = str(db_path)

    with app.test_client() as flask_client:
        yield flask_client, db_path


def test_login_page_renders(client) -> None:
    flask_client, _ = client
    response = flask_client.get("/login")

    assert response.status_code == 200
    assert b"Login" in response.data


def test_successful_login_redirects_home(client) -> None:
    flask_client, db_path = client
    create_user_account(email="valid@example.com", password="pass1234", db_path=db_path)

    response = flask_client.post(
        "/login",
        data={"email": "valid@example.com", "password": "pass1234"},
        follow_redirects=False,
    )

    assert response.status_code in {302, 303}
    assert "/?logged_in=1" in response.headers["Location"]


def test_invalid_login_shows_error(client) -> None:
    flask_client, _ = client
    response = flask_client.post(
        "/login",
        data={"email": "missing@example.com", "password": "pass1234"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_logout_signed_out_is_blocked(client) -> None:
    flask_client, _ = client
    response = flask_client.post("/logout")

    assert response.status_code == 403


def test_logout_invalidates_user_version(client) -> None:
    flask_client, db_path = client
    user_id = create_user_account(email="logout@example.com", password="pass1234", db_path=db_path)

    flask_client.post("/login", data={"email": "logout@example.com", "password": "pass1234"})

    with get_connection(db_path) as connection:
        before = connection.execute(
            "SELECT session_version FROM user_accounts WHERE id = ?",
            (user_id,),
        ).fetchone()[0]

    response = flask_client.post("/logout", follow_redirects=False)
    assert response.status_code in {302, 303}

    with get_connection(db_path) as connection:
        after = connection.execute(
            "SELECT session_version FROM user_accounts WHERE id = ?",
            (user_id,),
        ).fetchone()[0]

    assert after == before + 1


def test_favourites_nav_hidden_when_logged_out(client) -> None:
    flask_client, _ = client

    response = flask_client.get("/?fetch=1")

    assert response.status_code == 200
    assert b"Favourites" not in response.data


def test_favourites_route_not_found_when_logged_out(client) -> None:
    flask_client, _ = client

    response = flask_client.get("/favourites")

    assert response.status_code == 404
