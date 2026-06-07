from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.app import LATEST_RESULTS, app
from src.services.db import init_db
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


@patch("src.app.fetch_items")
def test_homepage_displays_results(mock_fetch: Mock, client) -> None:
    flask_client, _ = client
    mock_fetch.return_value = SAMPLE_RESULT

    response = flask_client.get("/?source=arxiv&fetch=1")
    assert response.status_code == 200
    assert b"Results from arXiv" in response.data
    assert b"Example Paper" in response.data
    assert b"View details" in response.data


@patch("src.app.fetch_items")
def test_detail_view_shows_source_link(mock_fetch: Mock, client) -> None:
    flask_client, _ = client
    mock_fetch.return_value = SAMPLE_RESULT
    flask_client.get("/?source=arxiv&fetch=1")

    response = flask_client.get("/detail/1234.5678v1?source=arxiv", follow_redirects=True)
    assert response.status_code == 200
    assert b"Open original source" in response.data
    assert b"https://arxiv.org/abs/1234.5678v1" in response.data


@patch("src.app.fetch_items")
def test_error_state_shows_retry(mock_fetch: Mock, client) -> None:
    flask_client, _ = client
    mock_fetch.return_value = {
        "source": "arxiv",
        "status": "error",
        "items": [],
        "error_message": "arXiv is unavailable.",
        "fetched_at": None,
    }

    response = flask_client.get("/?fetch=1")
    assert response.status_code == 200
    assert b"arXiv is unavailable." in response.data
    assert b"Retry" in response.data


@patch("src.app.fetch_items")
def test_home_button_visible(mock_fetch: Mock, client) -> None:
    flask_client, _ = client
    mock_fetch.return_value = SAMPLE_RESULT

    home_response = flask_client.get("/?fetch=1")
    assert home_response.status_code == 200
    assert b"Home" in home_response.data

    flask_client.get("/?fetch=1")
    detail_response = flask_client.get("/detail/1234.5678v1?source=arxiv", follow_redirects=True)
    assert detail_response.status_code == 200
    assert b"Home" in detail_response.data


@patch("src.app.fetch_items")
def test_detail_prompts_sign_in_for_favourites(mock_fetch: Mock, client) -> None:
    flask_client, _ = client
    mock_fetch.return_value = SAMPLE_RESULT
    flask_client.get("/?fetch=1")

    response = flask_client.get("/detail/1234.5678v1?source=arxiv")
    assert response.status_code == 200
    assert b"Sign in to save this paper to favourites." in response.data


@patch("src.app.fetch_items")
def test_unauthenticated_favourites_routes_return_not_found(mock_fetch: Mock, client) -> None:
    flask_client, _ = client
    mock_fetch.return_value = SAMPLE_RESULT

    flask_client.get("/?fetch=1")

    list_response = flask_client.get("/favourites")
    toggle_response = flask_client.post("/favourite/toggle", data={"item_id": "1234.5678v1", "source": "arxiv"})
    remove_response = flask_client.post("/favourite/remove", data={"item_id": "1234.5678v1", "source": "arxiv"})

    assert list_response.status_code == 404
    assert toggle_response.status_code == 404
    assert remove_response.status_code == 404


@patch("src.app.fetch_items")
def test_heart_toggle_adds_and_removes_for_authenticated_user(mock_fetch: Mock, client) -> None:
    flask_client, db_path = client
    mock_fetch.return_value = SAMPLE_RESULT
    create_user_account(email="owner@example.com", password="pass1234", db_path=db_path)
    _login(flask_client, email="owner@example.com")

    flask_client.get("/?fetch=1")

    added = flask_client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1", "source": "arxiv"},
        follow_redirects=True,
    )
    assert added.status_code == 200
    assert b"\xe2\x99\xa5" in added.data

    removed = flask_client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1", "source": "arxiv"},
        follow_redirects=True,
    )
    assert removed.status_code == 200
    assert b"\xe2\x99\xa1" in removed.data


@patch("src.app.fetch_items")
def test_favourite_persists_across_logout_login(mock_fetch: Mock, client) -> None:
    flask_client, db_path = client
    mock_fetch.return_value = SAMPLE_RESULT
    create_user_account(email="persist@example.com", password="pass1234", db_path=db_path)

    _login(flask_client, email="persist@example.com")
    flask_client.get("/?fetch=1")
    flask_client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1", "source": "arxiv"},
        follow_redirects=True,
    )

    flask_client.post("/logout")
    _login(flask_client, email="persist@example.com")

    response = flask_client.get("/favourites")
    assert response.status_code == 200
    assert b"Example Paper" in response.data


@patch("src.app.fetch_items")
def test_favourites_isolated_between_users(mock_fetch: Mock, client) -> None:
    flask_client, db_path = client
    mock_fetch.return_value = SAMPLE_RESULT
    create_user_account(email="usera@example.com", password="pass1234", db_path=db_path)
    create_user_account(email="userb@example.com", password="pass1234", db_path=db_path)

    _login(flask_client, email="usera@example.com")
    flask_client.get("/?fetch=1")
    flask_client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1", "source": "arxiv"},
        follow_redirects=True,
    )
    flask_client.post("/logout")

    _login(flask_client, email="userb@example.com")
    response = flask_client.get("/favourites")

    assert response.status_code == 200
    assert b"Example Paper" not in response.data
    assert b"No favourites saved yet" in response.data


@patch("src.app.fetch_items")
def test_hamburger_menu_visibility_depends_on_auth(mock_fetch: Mock, client) -> None:
    flask_client, db_path = client
    mock_fetch.return_value = SAMPLE_RESULT
    create_user_account(email="menu@example.com", password="pass1234", db_path=db_path)

    logged_out = flask_client.get("/?fetch=1")
    assert b"\xe2\x98\xb0" in logged_out.data
    assert b"Favourites" not in logged_out.data

    _login(flask_client, email="menu@example.com")
    logged_in = flask_client.get("/?fetch=1")
    assert b"Favourites" in logged_in.data


@patch("src.app.fetch_items")
def test_favourites_page_shows_saved_papers(mock_fetch: Mock, client) -> None:
    flask_client, db_path = client
    mock_fetch.return_value = SAMPLE_RESULT
    create_user_account(email="show@example.com", password="pass1234", db_path=db_path)
    _login(flask_client, email="show@example.com")

    flask_client.get("/?fetch=1")
    flask_client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1", "source": "arxiv"},
        follow_redirects=True,
    )

    response = flask_client.get("/favourites")
    assert response.status_code == 200
    assert b"Favourites" in response.data
    assert b"Example Paper" in response.data
    assert b"Jane Doe" in response.data


@patch("src.app.fetch_items")
def test_remove_button_on_favourites_page(mock_fetch: Mock, client) -> None:
    flask_client, db_path = client
    mock_fetch.return_value = SAMPLE_RESULT
    create_user_account(email="remove@example.com", password="pass1234", db_path=db_path)
    _login(flask_client, email="remove@example.com")

    flask_client.get("/?fetch=1")
    flask_client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1", "source": "arxiv"},
        follow_redirects=True,
    )

    response = flask_client.post(
        "/favourite/remove",
        data={"item_id": "1234.5678v1", "source": "arxiv"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"No favourites saved yet" in response.data


@patch("src.app.fetch_items")
def test_empty_favourites_page_for_authenticated_user(mock_fetch: Mock, client) -> None:
    flask_client, db_path = client
    mock_fetch.return_value = SAMPLE_RESULT
    create_user_account(email="empty@example.com", password="pass1234", db_path=db_path)
    _login(flask_client, email="empty@example.com")

    response = flask_client.get("/favourites")
    assert response.status_code == 200
    assert b"No favourites saved yet" in response.data


@patch("src.app.fetch_items")
def test_detail_view_from_favourites_fallback(mock_fetch: Mock, client) -> None:
    flask_client, db_path = client
    mock_fetch.return_value = SAMPLE_RESULT
    create_user_account(email="fallback@example.com", password="pass1234", db_path=db_path)
    _login(flask_client, email="fallback@example.com")

    flask_client.get("/?fetch=1")
    flask_client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1", "source": "arxiv"},
        follow_redirects=True,
    )

    mock_fetch.return_value = {
        "source": "arxiv",
        "status": "success",
        "items": [],
        "error_message": None,
        "fetched_at": "2026-05-01T12:10:00+00:00",
    }
    flask_client.get("/?query=differentquery&fetch=1")

    response = flask_client.get("/detail/1234.5678v1?source=arxiv")
    assert response.status_code == 200
    assert b"Example Paper" in response.data
    assert b"Jane Doe" in response.data
