from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.app import LATEST_RESULTS, app
from src.services.db import init_db, set_user_interest_preferences
from src.services.registration_service import create_user_account

SAMPLE_RESULT = {
    "source": "arxiv",
    "status": "success",
    "items": [
        {
            "id": "1234.5678v1",
            "source": "arxiv",
            "title": "Example Paper",
            "authors": ["Jane Doe"],
            "summary": "Example summary.",
            "url": "https://arxiv.org/abs/1234.5678v1",
            "published_at": "2026-05-01T12:00:00+00:00",
            "source_label": "arXiv",
            "fetched_at": "2026-05-01T12:10:00+00:00",
        }
    ],
    "error_message": None,
    "fetched_at": "2026-05-01T12:10:00+00:00",
}


@pytest.fixture()
def client(tmp_path: Path):
    db_path = tmp_path / "discovery_integration.db"
    init_db(db_path)

    app.config["TESTING"] = True
    app.config["AUTH_DB_PATH"] = str(db_path)
    app.config["REGISTRATION_DB_PATH"] = str(db_path)

    LATEST_RESULTS["arxiv"] = []

    with app.test_client() as flask_client:
        yield flask_client, db_path


def _login(flask_client, email: str = "user@example.com", password: str = "pass1234") -> None:
    flask_client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


def _create_and_login_user(flask_client, db_path, email: str = "user@example.com") -> int:
    user_id = create_user_account(email=email, password="pass1234", db_path=db_path)
    _login(flask_client, email=email)
    return user_id


def _set_onboarded(user_id: int, db_path, keys: list[str] | None = None) -> None:
    selected = keys or ["cs.ai", "cs.cv", "cs.lg"]
    set_user_interest_preferences(
        user_id=user_id,
        interest_keys=selected,
        onboarding_completed=True,
        db_path=db_path,
    )


@patch("src.app.fetch_items")
def test_homepage_displays_results_for_signed_out_user(mock_fetch: Mock, client) -> None:
    flask_client, _ = client
    mock_fetch.return_value = SAMPLE_RESULT

    response = flask_client.get("/?source=arxiv&fetch=1")
    assert response.status_code == 200
    assert b"Results from arXiv" in response.data
    assert b"Example Paper" in response.data


@patch("src.app.fetch_items")
def test_authenticated_user_without_onboarding_is_redirected(mock_fetch: Mock, client) -> None:
    flask_client, db_path = client
    mock_fetch.return_value = SAMPLE_RESULT
    _create_and_login_user(flask_client, db_path, email="gate@example.com")

    response = flask_client.get("/?fetch=1", follow_redirects=False)

    assert response.status_code in {302, 303}
    assert "/onboarding/interests" in response.headers["Location"]


def test_onboarding_page_renders_for_authenticated_user(client) -> None:
    flask_client, db_path = client
    _create_and_login_user(flask_client, db_path, email="onboard@example.com")

    response = flask_client.get("/onboarding/interests")

    assert response.status_code == 200
    assert b"Choose your interests" in response.data


def test_onboarding_submit_rejects_invalid_selection_count(client) -> None:
    flask_client, db_path = client
    _create_and_login_user(flask_client, db_path, email="invalid@example.com")

    response = flask_client.post(
        "/onboarding/interests",
        data={"interest_keys": ["cs.ai", "cs.cv"]},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Please choose at least 3 interests." in response.data


@patch("src.app.fetch_items")
def test_onboarding_submit_allows_discovery_after_completion(mock_fetch: Mock, client) -> None:
    flask_client, db_path = client
    mock_fetch.return_value = SAMPLE_RESULT
    _create_and_login_user(flask_client, db_path, email="complete@example.com")

    submit = flask_client.post(
        "/onboarding/interests",
        data={"interest_keys": ["cs.ai", "cs.cv", "cs.lg"]},
        follow_redirects=False,
    )
    assert submit.status_code in {302, 303}

    home_response = flask_client.get("/?fetch=1")
    assert home_response.status_code == 200


def test_interest_management_prepopulates_current_selection(client) -> None:
    flask_client, db_path = client
    user_id = _create_and_login_user(flask_client, db_path, email="manage@example.com")
    _set_onboarded(user_id, db_path, ["cs.ai", "cs.cv", "cs.lg"])

    response = flask_client.get("/interests")

    assert response.status_code == 200
    assert b"Manage interests" in response.data
    assert b"cs.ai" in response.data


def test_interest_management_update_persists(client) -> None:
    flask_client, db_path = client
    user_id = _create_and_login_user(flask_client, db_path, email="update@example.com")
    _set_onboarded(user_id, db_path, ["cs.ai", "cs.cv", "cs.lg"])

    response = flask_client.post(
        "/interests",
        data={"interest_keys": ["cs.ai", "cs.cl", "cs.db"]},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"cs.cl" in response.data


@patch("src.app.fetch_items")
def test_discovery_defaults_use_or_query(mock_fetch: Mock, client) -> None:
    flask_client, db_path = client
    mock_fetch.return_value = SAMPLE_RESULT
    user_id = _create_and_login_user(flask_client, db_path, email="or@example.com")
    _set_onboarded(user_id, db_path, ["cs.ai", "cs.cv", "cs.lg"])

    response = flask_client.get("/?fetch=1")

    assert response.status_code == 200
    called_query = mock_fetch.call_args.kwargs.get("query")
    assert "cat:cs.ai" in called_query
    assert "OR" in called_query


@patch("src.app.fetch_items")
def test_manual_query_overrides_interest_defaults(mock_fetch: Mock, client) -> None:
    flask_client, db_path = client
    mock_fetch.return_value = SAMPLE_RESULT
    user_id = _create_and_login_user(flask_client, db_path, email="override@example.com")
    _set_onboarded(user_id, db_path)

    response = flask_client.get("/?query=graph+neural+networks&fetch=1")

    assert response.status_code == 200
    assert mock_fetch.call_args.kwargs.get("query") == "graph neural networks"


@patch("src.app.fetch_items")
def test_favourites_still_work_for_onboarded_user(mock_fetch: Mock, client) -> None:
    flask_client, db_path = client
    mock_fetch.return_value = SAMPLE_RESULT
    user_id = _create_and_login_user(flask_client, db_path, email="fav@example.com")
    _set_onboarded(user_id, db_path)

    flask_client.get("/?fetch=1")
    flask_client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1", "source": "arxiv"},
        follow_redirects=True,
    )

    response = flask_client.get("/favourites")
    assert response.status_code == 200
    assert b"Example Paper" in response.data


def test_unauthenticated_interest_routes_redirect_to_login(client) -> None:
    flask_client, _ = client

    onboarding = flask_client.get("/onboarding/interests", follow_redirects=False)
    manage = flask_client.get("/interests", follow_redirects=False)

    assert onboarding.status_code in {302, 303}
    assert "/login" in onboarding.headers["Location"]
    assert manage.status_code in {302, 303}
    assert "/login" in manage.headers["Location"]
