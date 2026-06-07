# API Contract: Standardize arXiv Discovery Source (v1)

**Feature**: 007-rework-arxiv-lib  
**Date**: 2026-06-04

## Scope

This contract describes externally observable behavior for discovery and detail data served by the existing Flask app after migration to the Python `arxiv` library.

## GET /api/listings

Fetch normalized discovery results.

### Request

Query parameters:
- `source` (required): must be `arxiv`
- `query` (optional): free text query

### Response: Success

- Status: `200`
- Body:

```json
{
  "source": "arxiv",
  "status": "success",
  "items": [
    {
      "id": "2401.12345v2",
      "source": "arxiv",
      "title": "Example title",
      "authors": ["Author One"],
      "summary": "Example summary",
      "url": "https://arxiv.org/abs/2401.12345v2",
      "published_at": "2026-01-01T12:00:00+00:00",
      "source_label": "arXiv",
      "fetched_at": "2026-06-04T10:00:00+00:00",
      "metadata": {
        "primary_category": "cs.AI"
      }
    }
  ],
  "error_message": null,
  "fetched_at": "2026-06-04T10:00:00+00:00"
}
```

### Response: Empty

- Status: `200`
- Body `status` is `empty`
- `items` is empty
- `error_message` is `null`

### Response: Source error or timeout

- Status: `503`
- Body `status` is `error`
- `items` is empty
- `error_message` contains a non-sensitive message suitable for retry UX (`arXiv request timed out. Please retry.` for timeout paths)

### Validation guarantees

- `id` MUST be arXiv ID and canonical key.
- Every returned item MUST include required fields: `title`, `authors`, `summary`, `published_at`, `id`, `url`.
- Records with malformed required fields MUST be excluded.
- If any valid records remain after filtering malformed records, response MUST still be `status=success`.
- Source retrieval timeout MUST trigger error behavior at 4 seconds.

## GET /

Server-rendered discovery page.

- With `fetch=1`, page MUST render one of: success results, no-results state, or retry-ready error state.
- On timeout or source failure, page MUST display retry option without crashing.

## GET /detail/<item_id>

Server-rendered paper detail page.

- `item_id` lookup key is canonical arXiv ID.
- For known item, response is `200` and required detail content is visible.
- For unknown item, response is `404`.

## Compatibility constraints

- Existing route names and high-level workflows remain unchanged.
- Favorites eligibility behavior remains unchanged and keyed by canonical identifier.
