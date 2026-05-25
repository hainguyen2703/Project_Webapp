from unittest.mock import patch

import pytest

from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        yield client


def test_get_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"<form" in response.data


@patch("src.app.login_user", return_value=(1, None))
def test_post_login_valid_credentials(mock_login, client):
    with client.session_transaction() as sess:
        sess.clear()

    response = client.post(
        "/login",
        data={"email": "user@gmail.com", "password": "correct123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with client.session_transaction() as sess:
        assert sess["user_id"] == 1


@patch("src.app.login_user", return_value=(None, "Invalid email or password."))
def test_post_login_invalid_credentials(mock_login, client):
    response = client.post(
        "/login",
        data={"email": "user@gmail.com", "password": "wrong"},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_post_logout(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.post("/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_login_redirects_when_authenticated(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.get("/login", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_register_redirects_when_authenticated(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.get("/register", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_nav_shows_logout_when_logged_in(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.get("/")
    assert response.status_code == 200
    assert b"Log out" in response.data
    assert b"Login" not in response.data or b'href="/login"' not in response.data
