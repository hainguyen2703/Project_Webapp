# Data Model: User-Owned Favourites

**Feature**: 008-user-owned-favourites  
**Date**: 2026-06-07

## Entity: UserAccount

Represents an authenticated account that owns favourites.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | integer | Primary key | Existing `user_accounts.id` |
| `email` | string | Required, unique | Existing identity field |
| `is_active` | integer/bool | Required | Existing account lifecycle flag |
| `session_version` | integer | Required | Existing auth invalidation mechanism |

## Entity: FavouriteItem

Represents one saved paper owned by exactly one user.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | integer | Primary key | Internal row ID |
| `user_id` | integer | Required, FK -> `user_accounts.id` | Ownership boundary |
| `source` | string | Required | Example: `arxiv` |
| `external_paper_id` | string | Required | Canonical source ID used for dedupe |
| `title` | string | Required, non-empty | Display field |
| `authors_json` | string/json | Required | Serialized ordered author list |
| `summary` | string | Required, non-empty | Detail content fallback |
| `url` | string | Required, absolute URL | Source link |
| `published_at` | string | Required, ISO-8601 | Paper metadata |
| `source_label` | string | Required | Display label |
| `created_at` | string | Required, ISO-8601 UTC | Ordering key (most recent first) |
| `updated_at` | string | Required, ISO-8601 UTC | Mutation auditing support |

## Entity: FavouriteView

Projection used by templates/routes for rendering favourites.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `source` | string | Required | Used with external ID for linking |
| `external_paper_id` | string | Required | Used in route and duplicate checks |
| `title` | string | Required | List display |
| `authors` | list[string] | Required | Parsed from `authors_json` |
| `summary` | string | Required | Detail fallback |
| `url` | string | Required | Source link |
| `published_at` | string | Required | Detail display |
| `source_label` | string | Required | Badge/label |
| `created_at` | string | Required | Sort indicator |

## Relationships

- One `UserAccount` has zero-to-many `FavouriteItem` rows.
- Each `FavouriteItem` belongs to exactly one `UserAccount`.
- Multiple users may store the same `(source, external_paper_id)` independently.

## Validation Rules

- `(user_id, source, external_paper_id)` MUST be unique.
- `user_id` MUST reference an existing active user account at time of create/remove/list operations.
- Favourites list queries MUST return rows ordered by `created_at DESC`.
- Unauthenticated contexts MUST not return favourites data.
- Deleting a user account MUST immediately remove all owned favourites.

## State Transitions

1. `NotSaved` -> `Saved`: authenticated user adds favourite; row inserted.
2. `Saved` -> `Removed`: authenticated user removes favourite; row deleted.
3. `Saved` -> `Saved` (idempotent): repeated add for same `(user_id, source, external_paper_id)` does not create duplicate.
4. `Any` -> `Inaccessible`: unauthenticated request path receives generic not-found response for favourites routes.
5. `Saved` -> `DeletedByAccountRemoval`: account deletion cascades to owned favourites.

## Indexing and Integrity

- Unique index: `ux_favourites_owner_paper(user_id, source, external_paper_id)`.
- Access index: `ix_favourites_owner_created(user_id, created_at DESC)` for list performance.
- Foreign key: `favourite_items.user_id REFERENCES user_accounts(id) ON DELETE CASCADE`.
