from unittest.mock import Mock, patch

from src.app import app

SAMPLE_RESULT = {
    "source": "arxiv",
    "status": "success",
    "items": [
        {
            "id": "http://arxiv.org/abs/1234.5678v1",
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


@patch("src.app.fetch_items")
def test_homepage_displays_results(mock_fetch: Mock):
    mock_fetch.return_value = SAMPLE_RESULT
    client = app.test_client()

    response = client.get("/?source=arxiv&fetch=1")
    assert response.status_code == 200
    assert b"Results from arXiv" in response.data
    assert b"Example Paper" in response.data
    assert b"View details" in response.data


@patch("src.app.fetch_items")
def test_detail_view_shows_source_link(mock_fetch: Mock):
    mock_fetch.return_value = SAMPLE_RESULT
    client = app.test_client()
    client.get("/?source=arxiv&fetch=1")

    response = client.get(
        "/detail/http://arxiv.org/abs/1234.5678v1?source=arxiv",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Open original source" in response.data
    assert b"https://arxiv.org/abs/1234.5678v1" in response.data


@patch("src.app.fetch_items")
def test_error_state_shows_retry(mock_fetch: Mock):
    mock_fetch.return_value = {
        "source": "arxiv",
        "status": "error",
        "items": [],
        "error_message": "arXiv is unavailable.",
        "fetched_at": None,
    }
    client = app.test_client()

    response = client.get("/?fetch=1")
    assert response.status_code == 200
    assert b"arXiv is unavailable." in response.data
    assert b"Retry" in response.data


@patch("src.app.fetch_items")
def test_home_button_visible(mock_fetch: Mock):
    mock_fetch.return_value = SAMPLE_RESULT
    client = app.test_client()

    # Home button visible on the home page
    home_response = client.get("/?fetch=1")
    assert home_response.status_code == 200
    assert b"Home" in home_response.data

    # Seed LATEST_RESULTS so the detail page can find the item
    client.get("/?fetch=1")
    detail_response = client.get(
        "/detail/http://arxiv.org/abs/1234.5678v1?source=arxiv",
        follow_redirects=True,
    )
    assert detail_response.status_code == 200
    assert b"Home" in detail_response.data
