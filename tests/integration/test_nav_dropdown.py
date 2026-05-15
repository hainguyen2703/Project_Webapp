"""Integration tests for the navigation dropdown (feature 003).

Tests verify server-rendered HTML structure only — JS toggle behaviour is
client-side and covered by manual acceptance tests in quickstart.md.
"""
import re

import pytest

from src.app import app
from src.models.user import db as _db


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["MAIL_SUPPRESS_SEND"] = True
    app.config["SECRET_KEY"] = "test-secret"
    with app.app_context():
        _db.create_all()
        with app.test_client() as c:
            yield c
        _db.drop_all()


# ---------------------------------------------------------------------------
# US1: Hamburger trigger visible on every page
# ---------------------------------------------------------------------------

def test_trigger_button_present_on_home(client):
    """US1: GET / renders the hamburger trigger button."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'id="menu-trigger"' in html


def test_trigger_aria_label_menu(client):
    """US1: Trigger button carries aria-label='Menu'."""
    html = client.get("/").get_data(as_text=True)
    assert 'aria-label="Menu"' in html


def test_trigger_aria_expanded_false_on_load(client):
    """US1: aria-expanded is 'false' on initial render (dropdown closed)."""
    html = client.get("/").get_data(as_text=True)
    assert 'aria-expanded="false"' in html


def test_trigger_aria_controls_menu_dropdown(client):
    """US1: Trigger references the dropdown via aria-controls."""
    html = client.get("/").get_data(as_text=True)
    assert 'aria-controls="menu-dropdown"' in html


def test_existing_header_content_intact(client):
    """US1/SC-001: h1 and subtitle paragraph still present — no regression."""
    html = client.get("/").get_data(as_text=True)
    assert "Paper Discovery" in html
    assert "Choose a source" in html


def test_trigger_present_on_register_page(client):
    """US1/FR-001: Dropdown trigger renders on the /register page too."""
    html = client.get("/register").get_data(as_text=True)
    assert 'id="menu-trigger"' in html


# ---------------------------------------------------------------------------
# US2: Register link inside the dropdown
# ---------------------------------------------------------------------------

def test_dropdown_nav_present(client):
    """US2: nav#menu-dropdown element is present in rendered HTML."""
    html = client.get("/").get_data(as_text=True)
    assert 'id="menu-dropdown"' in html


def test_dropdown_hidden_by_default(client):
    """US2: Dropdown has class 'nav-dropdown' but NOT 'open' on initial load."""
    html = client.get("/").get_data(as_text=True)
    # The nav element must not carry the 'open' class on first render
    nav_match = re.search(r'<nav[^>]*id="menu-dropdown"[^>]*>', html)
    assert nav_match is not None, "nav#menu-dropdown not found"
    assert "open" not in nav_match.group(0)


def test_register_link_inside_dropdown(client):
    """US2/FR-002: Dropdown contains href='/register' with 'Register' text."""
    html = client.get("/").get_data(as_text=True)
    dropdown_match = re.search(
        r'<nav[^>]*id="menu-dropdown"[^>]*>.*?</nav>', html, re.DOTALL
    )
    assert dropdown_match is not None, "nav#menu-dropdown not found"
    dropdown_html = dropdown_match.group(0)
    assert 'href="/register"' in dropdown_html
    assert "Register" in dropdown_html


def test_register_link_present_on_every_listed_route(client):
    """US2/SC-002: Register link reachable from all existing routes."""
    for path in ["/", "/register"]:
        html = client.get(path).get_data(as_text=True)
        assert 'href="/register"' in html, f"Register link missing on {path}"


def test_no_future_feature_messaging(client):
    """FR-005: No 'coming soon' or 'requires account' text shown to guests."""
    html = client.get("/").get_data(as_text=True)
    assert "coming soon" not in html.lower()
    assert "requires account" not in html.lower()
    assert "unlock" not in html.lower()
