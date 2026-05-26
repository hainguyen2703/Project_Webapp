# Quickstart: Simplify to arXiv-Only Source

**Feature**: 003-arxiv-only-source  
**Date**: 2026-05-26

---

## Prerequisites

- Python 3.x installed
- pip available

---

## Setup

```bash
# Clone / navigate to the project root
cd d:\Project\Project_Webapp

# Install dependencies
pip install -r requirements.txt
```

---

## Run the Application

```bash
python -m src.app
```

The app starts on **http://localhost:8000**.

---

## Using the App

1. Open **http://localhost:8000** in a browser.
2. Optionally enter a search keyword in the **Search term** field.
3. Click **Fetch Listings** — arXiv papers matching the keyword appear as cards.
4. Click **View details** on any card to see the full paper detail page.
5. Click the **Home** button (visible in the header on every page) to return to the home page with a fresh arXiv fetch.

---

## Run Tests

```bash
pytest tests/
```

Expected output: all tests pass with no Medium-related test failures.

---

## Key Files Changed in This Feature

| File | Change |
|------|--------|
| `src/clients/medium_client.py` | Deleted |
| `src/services/discovery_service.py` | Removed Medium import and `elif source == "medium"` branch |
| `src/app.py` | Removed `CONTENT_SOURCES`; simplified `LATEST_RESULTS`; hardcoded `source = "arxiv"` |
| `src/templates/base.html` | Added "Home" button anchor to the header |
| `src/templates/home.html` | Removed source `<select>` dropdown |
| `src/templates/detail.html` | Simplified "Return to list" link (removed `source` param) |
| `tests/unit/test_source_clients.py` | Removed Medium client import and test |
| `tests/integration/test_discovery_flow.py` | Updated error test; added Home button visibility test |
