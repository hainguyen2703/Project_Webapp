# API Contract: Paper Discovery Web App (v2 — arXiv Only)

**Feature**: 003-arxiv-only-source  
**Date**: 2026-05-26  
**Breaking change**: `source=medium` no longer returns results; see §Removed below.

---

## Endpoints

### GET /

Renders the home page with the arXiv paper feed.

**Query parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `fetch` | `string` | No | Any truthy value (e.g., `"1"`) triggers a fresh arXiv fetch |
| `query` | `string` | No | Optional keyword to filter arXiv results |

> The `source` query parameter is **ignored**. arXiv is always used as the sole source.

**Responses**:

| Condition | HTTP Status | Rendered content |
|-----------|-------------|-----------------|
| `fetch` absent | 200 | Home page with no results (empty feed) |
| `fetch` present, arXiv returns results | 200 | Home page with paper cards |
| `fetch` present, arXiv returns empty | 200 | Home page with "No results" message |
| `fetch` present, arXiv request fails | 200 | Home page with error message and Retry link |

---

### GET /api/listings

JSON endpoint for fetching paper listings programmatically.

**Query parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `source` | `string` | Yes | Must be `"arxiv"`. Any other value returns an error response. |
| `query` | `string` | No | Optional keyword to filter arXiv results |

**Response schema**:

```json
{
  "source": "arxiv",
  "status": "success | empty | error",
  "items": [ PaperArticle ],
  "error_message": "string | null",
  "fetched_at": "ISO 8601 string | null"
}
```

**PaperArticle schema**:

```json
{
  "id": "string (URL)",
  "source": "arxiv",
  "title": "string",
  "authors": ["string"],
  "summary": "string",
  "url": "string (URL)",
  "published_at": "ISO 8601 string",
  "source_label": "arXiv",
  "fetched_at": "ISO 8601 string",
  "thumbnail_url": "string | null",
  "metadata": { "primary_category": "string" }
}
```

**HTTP status codes**:

| Condition | HTTP Status | `status` field |
|-----------|-------------|----------------|
| `source` missing | 400 | `"error"` |
| `source` is not `"arxiv"` | 503 | `"error"` |
| arXiv returns results | 200 | `"success"` |
| arXiv returns empty | 200 | `"empty"` |
| arXiv request fails | 503 | `"error"` |

---

### GET /detail/{item_id}

Renders the detail page for a specific paper.

**Path parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `item_id` | `string` (URL-encoded) | The arXiv paper ID (full URL, e.g., `http://arxiv.org/abs/1234.5678v1`) |

**Query parameters**:

> The `source` query parameter is accepted for backward compatibility but is effectively ignored — the detail view always looks up papers from `LATEST_RESULTS["arxiv"]`.

**Responses**:

| Condition | HTTP Status |
|-----------|-------------|
| Paper found in `LATEST_RESULTS["arxiv"]` | 200 |
| Paper not found | 404 |

---

## Removed in This Version

| Endpoint / Parameter | Removed Behaviour |
|----------------------|-------------------|
| `GET /?source=medium` | `source` param is silently ignored; arXiv results served instead |
| `GET /api/listings?source=medium` | Returns HTTP 503 with `status: "error"`, `error_message: "Unsupported source."` |
| Source dropdown in UI | Removed from `home.html`; no UI equivalent |
