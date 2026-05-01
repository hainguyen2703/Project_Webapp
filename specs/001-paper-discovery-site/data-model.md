# Data Model: Paper Discovery Website

## Entities

### ContentSource
- `id`: string
- `name`: string
- `display_name`: string
- `type`: enum(`arxiv`, `medium`)
- `fetch_endpoint`: string
- `description`: string

### PaperArticle
- `id`: string
- `source`: string (`arxiv` or `medium`)
- `title`: string
- `authors`: string[]
- `summary`: string
- `url`: string
- `published_at`: string (ISO 8601)
- `source_label`: string
- `thumbnail_url`: string? (optional)
- `fetched_at`: string (ISO 8601)
- `metadata`: object (optional source-specific fields)

### FetchResult
- `source`: string
- `items`: PaperArticle[]
- `status`: enum(`success`, `empty`, `error`)
- `error_message`: string?
- `fetched_at`: string

## Relationships
- One `ContentSource` can produce many `PaperArticle` items.
- The UI receives a `FetchResult` for a selected source and renders the `items` array.

## Validation Rules
- `source` MUST be either `arxiv` or `medium`.
- `title` MUST be non-empty.
- `url` MUST be a valid absolute URL.
- `published_at` MUST be a valid ISO 8601 timestamp.
- `summary` SHOULD be present, but the UI can render a fallback message if empty.
- `authors` SHOULD be an array of one or more author strings when available.

## Caching / Persistence Considerations
- MVP can use in-memory caching for the most recent results per source.
- If fetch latency or rate limits become problematic, add a lightweight cache store using SQLite.
- Cached `PaperArticle` records should include `fetched_at` to support freshness checks.

## Optional Future Data Model Extensions
- `user_preferences` to store preferred source or display mode.
- `topic` or `category` tags for filtering search results.
- `read_status` and `saved_for_later` fields for a richer reading experience.
