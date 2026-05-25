# API Contract: Remove Academia.edu — arXiv Only

**Feature**: `005-remove-academia-arxiv-only`  
**Date**: 2026-05-25  
**Type**: HTTP route contract (Flask, server-rendered + JSON API)

---

## Changed Routes

### `GET /`

**Purpose**: Home page — renders the search form and results.

**Before**:
- Accepted `source` query param (default `"arxiv"`)
- Passed `sources` (list) and `selected_source` to template
- Source dropdown rendered in HTML

**After**:
- `source` query param silently ignored; source is always `"arxiv"`
- `sources` and `selected_source` no longer in template context
- No source selector in rendered HTML

**Query parameters**:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | No | Search keyword passed to arXiv |
| `fetch` | `"1"` | No | When present, triggers arXiv fetch |
| `source` | string | No | **Silently ignored** — present for backward compatibility only |

**Response**: `200 OK` — HTML page. Source selector element absent. Results labelled "arXiv".

---

### `GET /api/listings`

**Purpose**: JSON API — fetches and returns arXiv articles.

**Before**:
- Required `source` query param; returned `400` if missing
- Dispatched to `fetch_medium_articles` or `fetch_arxiv_articles` based on source value
- Returned `503` on fetch error

**After**:
- Always fetches from arXiv; `source` param silently ignored
- No 400 error path for missing/invalid source

**Query parameters**:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `query` | string | No | Search keyword passed to arXiv |
| `source` | string | No | **Silently ignored** |

**Response schema** (unchanged):

```json
{
  "source": "arxiv",
  "status": "success" | "empty" | "error",
  "items": [ ... ],
  "error_message": null | "string",
  "fetched_at": "ISO8601 string" | null
}
```

| Status | HTTP code | When |
|---|---|---|
| `success` | `200` | Items returned |
| `empty` | `200` | No results found |
| `error` | `503` | arXiv fetch failed (network error, timeout, etc.) |

---

### `GET /detail/<item_id>`

**Purpose**: Detail page — renders a single arXiv article.

**Before**:
- Accepted `source` query param (default `"arxiv"`) to select cache key in `LATEST_RESULTS`
- 404 if item not found in the specified source's cache

**After**:
- `source` param silently ignored; always reads from `LATEST_RESULTS["arxiv"]`
- 404 if item not found in arXiv cache

**Query parameters**:

| Parameter | Type | Required | Description |
|---|---|---|---|
| `source` | string | No | **Silently ignored** |

**Response**: `200 OK` — HTML detail page, or `404` if article not in cache.

---

## Unchanged Routes

| Route | Change |
|---|---|
| `GET /register` | None |
| `POST /register` | None |
| `GET /check-email` | None |
| `GET /verify/<token>` | None |

---

## Removed Behaviour

| Behaviour | Was | Is Now |
|---|---|---|
| `GET /api/listings` with no `source` | `400 {"error": "Missing source parameter."}` | `200` arXiv results |
| `GET /api/listings?source=academia` | `503` error from discovery service | `200` arXiv results (param ignored) |
| `GET /?source=academia` | rendered academia option as selected | renders arXiv results (param ignored) |
| Source selector `<select>` in home page HTML | present | absent |
