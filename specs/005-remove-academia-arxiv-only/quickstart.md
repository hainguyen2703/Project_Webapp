# Quickstart: Remove Academia.edu — arXiv Only

**Feature**: `005-remove-academia-arxiv-only`  
**Date**: 2026-05-25

---

## What This Feature Does

Removes the Academia.edu integration entirely. The home page no longer shows a source selector dropdown — arXiv is the sole, implicit source. All three routes (`/`, `/api/listings`, `/detail/<id>`) are simplified to always use arXiv. The `academia_client.py` file and all Academia.edu references are deleted.

---

## Files Changed

| File | Change |
|---|---|
| `src/clients/academia_client.py` | DELETED |
| `src/services/discovery_service.py` | MODIFIED: remove academia import and branch |
| `src/app.py` | MODIFIED: remove `CONTENT_SOURCES`, simplify `LATEST_RESULTS`, hardcode source in all three routes |
| `src/templates/home.html` | MODIFIED: remove source selector, fix heading and URL params |
| `src/templates/detail.html` | MODIFIED: remove `source=source` from return link |
| `tests/unit/test_source_clients.py` | MODIFIED: remove academia fixture and test |
| `tests/integration/test_discovery_flow.py` | MODIFIED: update assertions for new route behaviour |

---

## Running the App

```powershell
# From repo root
python -m flask --app src.app run --debug
```

Open `http://127.0.0.1:5000/` in a browser.

---

## Manual Acceptance Tests

### AC-1: No source selector on home page (SC-001, FR-001)

1. Open `http://127.0.0.1:5000/`
2. Confirm **no dropdown / source selector** is visible
3. Confirm **"Academia.edu" does not appear** anywhere on the page

### AC-2: arXiv results load without source selection (SC-002, FR-004)

1. Leave the search field blank and click **Fetch Listings**
2. Confirm results appear labelled **"arXiv"** with title, authors, date, and summary

### AC-3: Keyword search works

1. Enter **"deep learning"** in the search field and click **Fetch Listings**
2. Confirm arXiv results related to the search term appear

### AC-4: Detail view works (SC-005, FR-005)

1. Fetch any results (AC-2)
2. Click **View details** on any result
3. Confirm the detail page loads with title, authors, summary, and a link to `arxiv.org`
4. Click **Return to list** — confirm navigation back to home page with results

### AC-5: `source=academia` silently ignored (SC-003, FR-003)

1. Navigate to `http://127.0.0.1:5000/api/listings?source=academia`
2. Confirm a **JSON response with arXiv results** is returned (not an error, not a stack trace)

### AC-6: Error state shown gracefully (FR-004 regression)

1. Disconnect from the internet (or proxy to a failing endpoint)
2. Click **Fetch Listings**
3. Confirm a user-friendly error message is shown — no stack trace

### AC-7: Registration and navigation unaffected (FR-006 regression)

1. Click the navigation menu trigger
2. Confirm the dropdown menu appears with the Register link
3. Navigate to `/register` and confirm the registration form loads

---

## Automated Tests

```powershell
# From repo root
python -m pytest tests/ -v
```

Expected: **48 tests passing** (49 minus the removed `test_fetch_academia_articles`).
