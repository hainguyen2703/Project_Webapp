# API Contract: Paper Discovery Website

## Purpose
Define the backend contract for source listing and item retrieval for the paper discovery website.

## Endpoints

### GET /api/listings
Fetch a list of items from the selected source.

#### Query Parameters
- `source` (required): `arxiv` or `medium`
- `query` (optional): free-text filter or search term
- `limit` (optional): integer, maximum number of items to return

#### Success Response (200)
```json
{
  "source": "arxiv",
  "status": "success",
  "items": [
    {
      "id": "arxiv-1234.5678",
      "source": "arxiv",
      "title": "Example Paper Title",
      "authors": ["Jane Doe", "John Smith"],
      "summary": "A short description of the paper.",
      "url": "https://arxiv.org/abs/1234.5678",
      "published_at": "2026-05-01T12:00:00Z",
      "source_label": "arXiv",
      "fetched_at": "2026-05-01T12:05:00Z"
    }
  ]
}
```

#### Empty Response (200)
```json
{
  "source": "medium",
  "status": "empty",
  "items": [],
  "error_message": null,
  "fetched_at": "2026-05-01T12:05:00Z"
}
```

#### Error Response (503)
```json
{
  "source": "medium",
  "status": "error",
  "items": [],
  "error_message": "Medium source is currently unavailable. Please retry.",
  "fetched_at": "2026-05-01T12:05:00Z"
}
```

## Notes
- The endpoint MUST normalize content from arXiv and Medium into the same `PaperArticle` shape.
- Missing or source-specific metadata can populate `metadata` or be omitted from the UI.
- The contract supports future caching or search query parameters without changing the item shape.
