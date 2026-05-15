"""Integration tests for the full registration flow."""
from datetime import datetime, timezone

import pytest

from src.app import app
from src.models.user import UserAccount, VerificationToken, db as _db


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["MAIL_SUPPRESS_SEND"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.app_context():
        _db.create_all()
        with app.test_client() as client:
            yield client
        _db.drop_all()


def _register(client, email="user@gmail.com", password="Password1", consent="on"):
    return client.post(
        "/register",
        data={"email": email, "password": password, "consent": consent},
        follow_redirects=False,
    )


def test_happy_path_register_redirects_to_check_email(client):
    response = _register(client)
    assert response.status_code == 302
    assert "/check-email" in response.headers["Location"]


def test_happy_path_check_email_page_loads(client):
    _register(client)
    response = client.get("/check-email")
    assert response.status_code == 200
    assert b"Check your email" in response.data


def test_happy_path_verify_activates_account(client):
    with app.app_context():
        _register(client)
        token = VerificationToken.query.first()
        assert token is not None
        response = client.get(f"/verify/{token.token_value}")
        assert response.status_code == 200
        assert b"verified" in response.data.lower()
        user = UserAccount.query.filter_by(email="user@gmail.com").first()
        assert user.status == "active"


def test_duplicate_email_rejected(client):
    _register(client, email="dup@gmail.com")
    response = _register(client, email="dup@gmail.com")
    assert response.status_code == 400
    assert b"already registered" in response.data


def test_non_gmail_rejected(client):
    response = _register(client, email="user@yahoo.com")
    assert response.status_code == 400
    assert b"Gmail" in response.data


def test_blank_email_rejected(client):
    response = _register(client, email="")
    assert response.status_code == 400
    assert b"required" in response.data.lower()


def test_weak_password_rejected(client):
    response = _register(client, password="weak")
    assert response.status_code == 400
    assert b"Password" in response.data


def test_unchecked_consent_rejected(client):
    response = _register(client, consent="")
    assert response.status_code == 400
    assert b"Privacy Policy" in response.data


def test_check_email_without_session_redirects(client):
    response = client.get("/check-email", follow_redirects=False)
    assert response.status_code == 302
    assert "/register" in response.headers["Location"]
