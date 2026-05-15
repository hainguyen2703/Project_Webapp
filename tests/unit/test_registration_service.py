"""Unit tests for registration_service.py"""
from datetime import datetime, timedelta, timezone

import pytest

from src.app import app
from src.models.user import UserAccount, VerificationToken, db as _db
from src.models.user import db  # noqa: F401 – used via db.session.get
from src.services.registration_service import (
    _purge_expired_pending_accounts,
    register_user,
    resend_verification,
    validate_registration_input,
    verify_account,
)


@pytest.fixture()
def test_app():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["MAIL_SUPPRESS_SEND"] = True
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


# ── validate_registration_input ────────────────────────────────────────────────

def test_validate_blank_email(test_app):
    with test_app.app_context():
        errors = validate_registration_input("", "Password1", "on")
        assert "email" in errors


def test_validate_malformed_email(test_app):
    with test_app.app_context():
        errors = validate_registration_input("notanemail", "Password1", "on")
        assert "email" in errors


def test_validate_non_gmail_domain(test_app):
    with test_app.app_context():
        errors = validate_registration_input("user@yahoo.com", "Password1", "on")
        assert "email" in errors
        assert "Gmail" in errors["email"]


def test_validate_password_too_short(test_app):
    with test_app.app_context():
        errors = validate_registration_input("user@gmail.com", "Pw1", "on")
        assert "password" in errors


def test_validate_password_no_digit(test_app):
    with test_app.app_context():
        errors = validate_registration_input("user@gmail.com", "PasswordOnly", "on")
        assert "password" in errors


def test_validate_consent_not_checked(test_app):
    with test_app.app_context():
        errors = validate_registration_input("user@gmail.com", "Password1", "")
        assert "consent" in errors


def test_validate_valid_input_no_errors(test_app):
    with test_app.app_context():
        errors = validate_registration_input("user@gmail.com", "Password1", "on")
        assert errors == {}


# ── register_user ──────────────────────────────────────────────────────────────

def test_register_user_creates_account(test_app):
    with test_app.app_context():
        now = datetime.now(timezone.utc)
        result, user, token = register_user("new@gmail.com", "Password1", now)
        assert result == "ok"
        assert user is not None
        assert user.status == "pending"
        assert user.email == "new@gmail.com"
        assert token is not None
        assert token.resend_count == 0


def test_register_user_duplicate_rejected(test_app):
    with test_app.app_context():
        now = datetime.now(timezone.utc)
        register_user("dup@gmail.com", "Password1", now)
        result, user, token = register_user("dup@gmail.com", "Password1", now)
        assert result == "duplicate"
        assert user is None


# ── _purge_expired_pending_accounts ───────────────────────────────────────────

def test_purge_removes_expired_pending(test_app):
    with test_app.app_context():
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        user = UserAccount(
            email="old@gmail.com",
            password_hash="x",
            status="pending",
            created_at=old_time,
            consent_at=old_time,
        )
        _db.session.add(user)
        _db.session.commit()
        uid = user.id
        _purge_expired_pending_accounts()
        assert db.session.get(UserAccount, uid) is None


def test_purge_keeps_active_accounts(test_app):
    with test_app.app_context():
        old_time = datetime.now(timezone.utc) - timedelta(hours=25)
        user = UserAccount(
            email="active@gmail.com",
            password_hash="x",
            status="active",
            created_at=old_time,
            consent_at=old_time,
            verified_at=old_time,
        )
        _db.session.add(user)
        _db.session.commit()
        uid = user.id
        _purge_expired_pending_accounts()
        assert db.session.get(UserAccount, uid) is not None


# ── verify_account ─────────────────────────────────────────────────────────────

def test_verify_account_activates(test_app):
    with test_app.app_context():
        now = datetime.now(timezone.utc)
        _, user, token = register_user("verify@gmail.com", "Password1", now)
        result = verify_account(token.token_value)
        assert result == "activated"
        _db.session.refresh(user)
        assert user.status == "active"


def test_verify_account_already_used(test_app):
    with test_app.app_context():
        now = datetime.now(timezone.utc)
        _, user, token = register_user("used@gmail.com", "Password1", now)
        verify_account(token.token_value)
        result = verify_account(token.token_value)
        assert result == "already_used"


def test_verify_account_expired(test_app):
    with test_app.app_context():
        now = datetime.now(timezone.utc)
        _, user, token = register_user("expired@gmail.com", "Password1", now)
        token.expires_at = now - timedelta(hours=1)
        _db.session.commit()
        result = verify_account(token.token_value)
        assert result == "expired"


def test_verify_account_not_found(test_app):
    with test_app.app_context():
        result = verify_account("nonexistent_token_value")
        assert result == "not_found"


# ── resend_verification ────────────────────────────────────────────────────────

def test_resend_increments_count(test_app):
    with test_app.app_context():
        now = datetime.now(timezone.utc)
        _, user, token = register_user("resend@gmail.com", "Password1", now)
        # Move created_at back past cooldown
        token.created_at = now - timedelta(seconds=61)
        _db.session.commit()

        from unittest.mock import MagicMock
        mock_mail = MagicMock()
        result, _ = resend_verification(user.id, mock_mail)
        assert result == "sent"
        _db.session.refresh(token)
        assert token.resend_count == 1


def test_resend_cooldown_enforced(test_app):
    with test_app.app_context():
        now = datetime.now(timezone.utc)
        _, user, token = register_user("cooldown@gmail.com", "Password1", now)
        # token.created_at is 'now', cooldown not elapsed
        from unittest.mock import MagicMock
        mock_mail = MagicMock()
        result, _ = resend_verification(user.id, mock_mail)
        assert result == "cooldown"


def test_resend_limit_reached(test_app):
    with test_app.app_context():
        now = datetime.now(timezone.utc)
        _, user, token = register_user("limit@gmail.com", "Password1", now)
        token.resend_count = 3
        _db.session.commit()
        from unittest.mock import MagicMock
        mock_mail = MagicMock()
        result, _ = resend_verification(user.id, mock_mail)
        assert result == "limit_reached"
