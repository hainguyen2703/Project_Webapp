# Quickstart: Hamburger Menu with Favourites

**Feature**: 004-hamburger-favourites  
**Date**: 2026-05-26

---

## Prerequisites

- Python 3.x installed
- pip available

---

## Setup

```bash
cd d:\Project\Project_Webapp
pip install -r requirements.txt
```

---

## Run the Application

```bash
python -m src.app
```

App starts on **http://localhost:8000**.

---

## Using the Favourites Feature

### Save a paper

1. Open **http://localhost:8000** and click **Fetch Listings** to load arXiv papers.
2. Click **View details** on any paper card.
3. On the detail page, click the heart button (♡) — it fills (♥) to confirm the paper is saved.

### Remove a paper via heart toggle

1. On any detail page where the heart is filled (♥), click it again.
2. The heart returns to unfilled (♡) and the paper is removed from favourites.

### Access the Favourites page

1. Click the hamburger icon **☰** in the top-right of the header on any page.
2. Select **Favourites** from the revealed navigation menu.
3. All saved papers are listed, most recently saved first.
4. Click a paper's title to open its full detail view.
5. Click **×** next to any paper to remove it from favourites directly.

### Verify detail view from Favourites

1. Save a paper, then click **Fetch Listings** with a different keyword to change `LATEST_RESULTS`.
2. Open the Favourites page and click the saved paper's title.
3. The full detail view renders correctly from stored data, not from the new search results.

---

## Run Tests

```bash
pytest tests/
```

All tests (including new favourites integration tests) must pass.

---

## Key Files Changed in This Feature

| File | Change |
|------|--------|
| `src/app.py` | Added `FAVOURITES_STORE`, `secret_key`, 3 new routes, updated `item_detail` |
| `src/templates/base.html` | Added hamburger checkbox toggle + nav |
| `src/templates/detail.html` | Added heart toggle form and `is_favourite` state |
| `src/templates/favourites.html` | New: favourites list with × remove forms |
| `src/static/styles.css` | Added hamburger, heart, favourites page styles |
| `tests/integration/test_discovery_flow.py` | Added 6 new favourites test functions |
