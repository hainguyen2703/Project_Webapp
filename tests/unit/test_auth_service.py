from __future__ import annotations

from pathlib import Path

import pytest

from src.services.auth_service import (
    AuthResult,
    FAILED_LOGIN_MAX_ATTEMPTS,
    authenticate_user,
    issue_session_expiry,
    is_throttled,
    register_failed_attempt,
    reset_auth_tracking,
    session_is_expired,
)
from src.services.registration_service import create_user_account
from src.services.db import init_db


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "auth_test.db"
    init_db(path)
    reset_auth_tracking()
    return path


def test_authenticate_user_success_for_registered_user(db_path: Path) -> None:
    create_user_account(email="user@example.com", password="pass1234", db_path=db_path)

    result: AuthResult = authenticate_user(
        email="user@example.com",
        password="pass1234",
        db_path=db_path,
    )

    assert result.success is True
    assert result.code == "success"
    assert result.user_id is not None


def test_authenticate_user_rejects_missing_fields(db_path: Path) -> None:
    missing_email = authenticate_user(email="", password="pass1234", db_path=db_path)
    missing_password = authenticate_user(email="user@example.com", password="", db_path=db_path)

    assert missing_email.success is False
    assert "email" in missing_email.errors
    assert missing_password.success is False
    assert "password" in missing_password.errors


def test_authenticate_user_rejects_invalid_credentials(db_path: Path) -> None:
    create_user_account(email="user@example.com", password="pass1234", db_path=db_path)

    result = authenticate_user(email="user@example.com", password="wrong123", db_path=db_path)

    assert result.success is False
    assert result.code == "invalid_credentials"


def test_failed_attempts_trigger_throttle() -> None:
    reset_auth_tracking()
    identity = "throttle@example.com"

    for _ in range(FAILED_LOGIN_MAX_ATTEMPTS):
        register_failed_attempt(identity)

    assert is_throttled(identity) is True


def test_session_expiry_helpers() -> None:
    expires_at = issue_session_expiry()
    assert session_is_expired(expires_at) is False
    assert session_is_expired(expires_at - 999999) is True
