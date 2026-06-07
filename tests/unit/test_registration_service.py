from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from src.services.db import add_favourite, delete_user_account, get_connection, init_db
from src.services.registration_service import (
    IN_FLIGHT_SUBMISSIONS,
    RegistrationResult,
    password_meets_policy,
    register_user,
    reset_submission_locks,
    verify_password,
)


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "test_app.db"
    init_db(path)
    reset_submission_locks()
    return path


def test_password_policy_accepts_minimum_valid_password() -> None:
    assert password_meets_policy("abc12345") is True


def test_password_policy_rejects_missing_numeric_or_letter() -> None:
    assert password_meets_policy("abcdefgh") is False
    assert password_meets_policy("12345678") is False


def test_register_user_creates_active_account_with_hashed_password(db_path: Path) -> None:
    result: RegistrationResult = register_user(
        email="new.user@example.com",
        password="abc12345",
        session_key="session-a",
        submission_token="token-a",
        db_path=db_path,
    )

    assert result.success is True
    assert result.user_id is not None

    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT email, password_hash, is_active FROM user_accounts WHERE id = ?",
            (result.user_id,),
        ).fetchone()

    assert row is not None
    assert row[0] == "new.user@example.com"
    assert row[2] == 1
    assert verify_password(row[1], "abc12345") is True


def test_register_user_rejects_email_with_whitespace(db_path: Path) -> None:
    result = register_user(
        email=" user@example.com ",
        password="abc12345",
        session_key="session-b",
        submission_token="token-b",
        db_path=db_path,
    )

    assert result.success is False
    assert result.code == "validation_error"
    assert "email" in result.errors


def test_register_user_rejects_duplicate_email(db_path: Path) -> None:
    first = register_user(
        email="dupe@example.com",
        password="abc12345",
        session_key="session-c",
        submission_token="token-c1",
        db_path=db_path,
    )
    second = register_user(
        email="dupe@example.com",
        password="abc12345",
        session_key="session-c",
        submission_token="token-c2",
        db_path=db_path,
    )

    assert first.success is True
    assert second.success is False
    assert second.code == "duplicate_email"


def test_register_user_rejects_duplicate_inflight_submission(db_path: Path) -> None:
    IN_FLIGHT_SUBMISSIONS["session-d:token-d"] = 9999999999.0

    blocked = register_user(
        email="inflight@example.com",
        password="abc12345",
        session_key="session-d",
        submission_token="token-d",
        db_path=db_path,
    )

    assert blocked.success is False
    assert blocked.code == "duplicate_submission"


def test_delete_user_account_cascades_favourites(db_path: Path) -> None:
    registered = register_user(
        email="cleanup@example.com",
        password="abc12345",
        session_key="session-e",
        submission_token="token-e",
        db_path=db_path,
    )
    assert registered.success is True
    assert registered.user_id is not None

    inserted = add_favourite(
        user_id=int(registered.user_id),
        source="arxiv",
        external_paper_id="1234.5678v1",
        paper={
            "title": "Cleanup Paper",
            "authors": ["Jane Doe"],
            "summary": "summary",
            "url": "https://arxiv.org/abs/1234.5678v1",
            "published_at": "2026-05-01T12:00:00+00:00",
            "source_label": "arXiv",
        },
        db_path=db_path,
    )
    assert inserted is True

    removed_user = delete_user_account(user_id=int(registered.user_id), db_path=db_path)
    assert removed_user is True

    with get_connection(db_path) as connection:
        favourite_count = connection.execute(
            "SELECT COUNT(*) FROM favourite_items WHERE user_id = ?",
            (int(registered.user_id),),
        ).fetchone()[0]

    assert favourite_count == 0
