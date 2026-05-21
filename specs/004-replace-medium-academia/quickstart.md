# Quickstart: Replace Medium Source with Academia.edu

**Feature**: `004-replace-medium-academia`  
**Date**: 2026-05-21

---

## What This Feature Does

Replaces the "Medium" source with "Academia.edu" throughout the application. The source selector now shows "Academia.edu" instead of "Medium". Selecting it fetches academic papers from Academia.edu's public search page via HTML scraping. All other sources (arXiv) and features (registration, navigation) are unaffected.

---

## Files Changed

| File | Change |
|---|---|
| `src/clients/academia_client.py` | NEW: Academia.edu HTML scraper using BeautifulSoup4 |
| `src/clients/medium_client.py` | DELETED |
| `src/services/discovery_service.py` | MODIFIED: replace `medium` branch with `academia` |
| `src/app.py` | MODIFIED: replace Medium entry in `CONTENT_SOURCES` and `LATEST_RESULTS` key |
| `tests/unit/test_source_clients.py` | MODIFIED: replace Medium test with Academia.edu fixture test |

---

## Running the App

```powershell
# From repo root with virtualenv active
flask --app src.app run --debug
```

Open `http://127.0.0.1:5000/` in a browser.

---

## Manual Acceptance Tests

### AC-1: Medium absent from source selector (SC-001)

1. Open `http://127.0.0.1:5000/`
2. Open the source dropdown
3. Confirm **"Medium" is not listed**; confirm **"Academia.edu" is listed**

### AC-2: Academia.edu fetch returns results (SC-002)

1. Select **Academia.edu** in the source dropdown
2. Leave the search field empty
3. Click **Fetch Listings**
4. Confirm results appear labelled **"Academia.edu"** with title, authors, date, and a snippet

### AC-3: Custom keyword search works

1. Select **Academia.edu**, enter **"deep learning"** in the search field
2. Click **Fetch Listings**
3. Confirm results are related to the search term

### AC-4: Error state shown gracefully (FR-006)

1. Disconnect from the internet (or proxy to a failing endpoint)
2. Select **Academia.edu** and click **Fetch Listings**
3. Confirm a user-friendly error message is shown — no stack trace

### AC-5: Detail view works for Academia.edu article (US2)

1. Fetch Academia.edu results (AC-2)
2. Click **View details** on any result
3. Confirm the detail page loads with title, authors, summary, and a link to the original Academia.edu URL

### AC-6: `source=medium` returns error response (SC-004)

1. Navigate directly to `http://127.0.0.1:5000/api/listings?source=medium`
2. Confirm a JSON error response is returned (not HTTP 500, no stack trace)

### AC-7: arXiv unaffected (SC-003 regression check)

1. Select **arXiv** and fetch results
2. Confirm arXiv results load normally

---

## Automated Tests

```powershell
# From repo root with virtualenv active
pytest tests/ -v
```

All pre-existing tests MUST pass. The `test_fetch_medium_articles` test is replaced by `test_fetch_academia_articles` in `tests/unit/test_source_clients.py`.
