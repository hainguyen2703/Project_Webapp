from unittest.mock import Mock, patch

from src.app import app

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
        "/detail/1234.5678v1?source=arxiv",
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
        "/detail/1234.5678v1?source=arxiv",
        follow_redirects=True,
    )
    assert detail_response.status_code == 200
    assert b"Home" in detail_response.data


@patch("src.app.fetch_items")
def test_heart_button_visible_on_detail_page(mock_fetch: Mock):
    """Test that the heart button appears on the detail page."""
    mock_fetch.return_value = SAMPLE_RESULT
    client = app.test_client()
    
    # Seed LATEST_RESULTS
    client.get("/?fetch=1")
    
    response = client.get("/detail/1234.5678v1?source=arxiv")
    assert response.status_code == 200
    # Unfilled heart (not favourited)
    assert b"\xe2\x99\xa1" in response.data  # ♡


@patch("src.app.fetch_items")
def test_heart_toggle_adds_to_favourites(mock_fetch: Mock):
    """Test clicking heart button adds paper to favourites."""
    mock_fetch.return_value = SAMPLE_RESULT
    client = app.test_client()
    
    # Seed LATEST_RESULTS
    client.get("/?fetch=1")
    
    # Toggle favourite (add)
    response = client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    # Filled heart (favourited)
    assert b"\xe2\x99\xa5" in response.data  # ♥


@patch("src.app.fetch_items")
def test_heart_toggle_removes_from_favourites(mock_fetch: Mock):
    """Test clicking heart button again removes paper from favourites."""
    mock_fetch.return_value = SAMPLE_RESULT
    client = app.test_client()
    
    # Seed LATEST_RESULTS
    client.get("/?fetch=1")
    
    # Toggle favourite (add)
    client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1"},
        follow_redirects=True,
    )
    
    # Toggle favourite (remove)
    response = client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    # Unfilled heart (not favourited)
    assert b"\xe2\x99\xa1" in response.data  # ♡


@patch("src.app.fetch_items")
def test_favourite_persists_across_page_loads(mock_fetch: Mock):
    """Test that favourited paper state persists across page loads."""
    mock_fetch.return_value = SAMPLE_RESULT
    client = app.test_client()
    
    # Seed LATEST_RESULTS
    client.get("/?fetch=1")
    
    # Add to favourites
    client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1"},
        follow_redirects=True,
    )
    
    # Load detail page again
    response = client.get("/detail/1234.5678v1?source=arxiv")
    assert response.status_code == 200
    # Still favourited
    assert b"\xe2\x99\xa5" in response.data  # ♥


@patch("src.app.fetch_items")
def test_hamburger_menu_visible(mock_fetch: Mock):
    """Test that hamburger menu appears on all pages."""
    mock_fetch.return_value = SAMPLE_RESULT
    client = app.test_client()
    
    # Home page
    home_response = client.get("/?fetch=1")
    assert b"\xe2\x98\xb0" in home_response.data  # ☰
    
    # Detail page
    detail_response = client.get("/detail/1234.5678v1?source=arxiv")
    assert b"\xe2\x98\xb0" in detail_response.data  # ☰
    
    # Favourites page
    fav_response = client.get("/favourites")
    assert b"\xe2\x98\xb0" in fav_response.data  # ☰


@patch("src.app.fetch_items")
def test_favourites_page_shows_saved_papers(mock_fetch: Mock):
    """Test that the Favourites page lists saved papers."""
    mock_fetch.return_value = SAMPLE_RESULT
    client = app.test_client()
    
    # Seed LATEST_RESULTS
    client.get("/?fetch=1")
    
    # Add to favourites
    client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1"},
        follow_redirects=True,
    )
    
    # Visit favourites page
    response = client.get("/favourites")
    assert response.status_code == 200
    assert b"Favourites" in response.data
    assert b"Example Paper" in response.data
    assert b"Jane Doe" in response.data


@patch("src.app.fetch_items")
def test_remove_button_on_favourites_page(mock_fetch: Mock):
    """Test that clicking × removes paper from favourites."""
    mock_fetch.return_value = SAMPLE_RESULT
    client = app.test_client()
    
    # Seed LATEST_RESULTS
    client.get("/?fetch=1")
    
    # Add to favourites
    client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1"},
        follow_redirects=True,
    )
    
    # Remove from favourites
    response = client.post(
        "/favourite/remove",
        data={"item_id": "1234.5678v1"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    # Empty state message
    assert b"No favourites saved yet" in response.data


@patch("src.app.fetch_items")
def test_empty_favourites_page(mock_fetch: Mock):
    """Test that Favourites page shows empty state when no papers saved."""
    mock_fetch.return_value = SAMPLE_RESULT
    client = app.test_client()
    
    response = client.get("/favourites")
    assert response.status_code == 200
    assert b"No favourites saved yet" in response.data


@patch("src.app.fetch_items")
def test_detail_view_from_favourites_fallback(mock_fetch: Mock):
    """Test that detail view works from favourites even after search results change."""
    mock_fetch.return_value = SAMPLE_RESULT
    client = app.test_client()
    
    # Seed LATEST_RESULTS
    client.get("/?fetch=1")
    
    # Add to favourites
    client.post(
        "/favourite/toggle",
        data={"item_id": "1234.5678v1"},
        follow_redirects=True,
    )
    
    # Clear LATEST_RESULTS by fetching with different query
    mock_fetch.return_value = {
        "source": "arxiv",
        "status": "success",
        "items": [],  # Empty results
        "error_message": None,
        "fetched_at": "2026-05-01T12:10:00+00:00",
    }
    client.get("/?query=differentquery&fetch=1")
    
    # Access detail page from favourites (should still work via fallback)
    response = client.get("/detail/1234.5678v1")
    assert response.status_code == 200
    assert b"Example Paper" in response.data
    assert b"Jane Doe" in response.data
