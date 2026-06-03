# Data Model: Standardize arXiv Discovery Source

**Feature**: 007-rework-arxiv-lib  
**Date**: 2026-06-04

## Entity: DiscoveryQuery

Represents user input that drives a retrieval request.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `query_text` | string | Optional, defaults to category fallback | User-entered search expression |
| `source` | string | Required, must be `arxiv` | Current feature scope is arXiv-only |
| `limit` | integer | Required, positive, bounded by service max | Number of requested items |
| `requested_at` | datetime (ISO-8601) | Required | For latency and retry correlation |

## Entity: PaperSummaryRecord

Canonical normalized record used by result lists and detail views.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | string | Required, arXiv ID only | Canonical identifier across flows |
| `source` | string | Required, `arxiv` | Source discriminator |
| `title` | string | Required, non-empty | Required content |
| `authors` | list[string] | Required, at least one normalized name | Required content |
| `summary` | string | Required, non-empty | Required content |
| `published_at` | string | Required, valid ISO-8601 | Required content |
| `url` | string | Required, absolute URL | Canonical paper link |
| `source_label` | string | Required, `arXiv` | Display label |
| `fetched_at` | string | Required, valid ISO-8601 | Retrieval timestamp |
| `metadata` | object | Optional | Includes optional tags/category |

## Entity: SourceRetrievalOutcome

Represents fetch-and-normalize result returned by discovery service.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `source` | string | Required | `arxiv` |
| `status` | enum | Required: `success`, `empty`, `error` | UI control state |
| `items` | list[PaperSummaryRecord] | Required | Contains only valid records |
| `error_message` | string | Optional | Present for error state |
| `fetched_at` | string | Optional | Null when nothing valid returned |

## Validation Rules

- Required detail content fields are: `title`, `authors`, `summary`, `published_at`, `id`, and `url`.
- `id` MUST be arXiv ID format and used as the canonical identity key.
- Records with malformed required fields MUST be excluded from output.
- Timeout at 4 seconds MUST produce `status=error` with retry-capable UX path.
- Empty valid-result set after filtering MUST produce `status=empty`.

## State Transitions

1. `DiscoveryQuery submitted` -> `SourceRetrievalOutcome.success` when at least one valid record remains.
2. `DiscoveryQuery submitted` -> `SourceRetrievalOutcome.empty` when source succeeds but yields no valid records.
3. `DiscoveryQuery submitted` -> `SourceRetrievalOutcome.error` on timeout or source failure.
4. `SourceRetrievalOutcome.error` -> `SourceRetrievalOutcome.success|empty` after user-triggered retry.

## Relationships

- One `DiscoveryQuery` produces one `SourceRetrievalOutcome`.
- One `SourceRetrievalOutcome` contains zero-to-many `PaperSummaryRecord` entries.
- `PaperSummaryRecord.id` is reused by detail and favorites flows as the stable lookup key.
