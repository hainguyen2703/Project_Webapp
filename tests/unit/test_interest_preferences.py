from __future__ import annotations

from pathlib import Path

import pytest

from src.services.db import (
    get_connection,
    init_db,
    is_onboarding_completed,
    list_user_interest_keys,
    reconcile_user_interests,
    set_user_interest_preferences,
)
from src.services.registration_service import create_user_account


@pytest.fixture()
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "interest_prefs.db"
    init_db(path)
    return path


def test_reconcile_removes_retired_and_autofills_defaults(db_path: Path) -> None:
    user_id = create_user_account(email="prefs@example.com", password="pass1234", db_path=db_path)
    set_user_interest_preferences(
        user_id=user_id,
        interest_keys=["cs.ai", "cs.cv", "cs.lg"],
        onboarding_completed=True,
        db_path=db_path,
    )

    with get_connection(db_path) as connection:
        connection.execute("UPDATE interest_topics SET is_active = 0 WHERE key = 'cs.cv'")
        connection.execute("UPDATE interest_topics SET is_active = 0 WHERE key = 'cs.lg'")

    reconciled = reconcile_user_interests(user_id=user_id, minimum_count=3, db_path=db_path)

    assert len(reconciled) >= 3
    assert "cs.cv" not in reconciled
    assert "cs.lg" not in reconciled
    assert "cs.ai" in reconciled


def test_reconcile_does_not_autofill_when_onboarding_incomplete(db_path: Path) -> None:
    user_id = create_user_account(email="incomplete@example.com", password="pass1234", db_path=db_path)
    set_user_interest_preferences(
        user_id=user_id,
        interest_keys=["cs.ai"],
        onboarding_completed=False,
        db_path=db_path,
    )

    reconciled = reconcile_user_interests(user_id=user_id, minimum_count=3, db_path=db_path)

    assert reconciled == list_user_interest_keys(user_id=user_id, active_only=True, db_path=db_path)
    assert len(reconciled) == 1
    assert is_onboarding_completed(user_id=user_id, db_path=db_path) is False
