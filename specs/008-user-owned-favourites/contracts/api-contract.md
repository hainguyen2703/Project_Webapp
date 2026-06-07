# API Contract: User-Owned Favourites (v1)

**Feature**: 008-user-owned-favourites  
**Date**: 2026-06-07

## Scope

This contract defines externally observable behavior for favourites ownership, access control, and persistence in the existing Flask app.

## Route: POST /favourite/toggle

Adds or removes a favourite for the currently authenticated user.

### Request

Form fields:
- `item_id` (required): source-specific paper identifier present in detail context

### Auth Behavior

- Authenticated: operation proceeds for `current_user.id`.
- Unauthenticated: route MUST not expose favourites functionality; response is generic not-found (`404`).

### Success Response

- Status: `302`/`303` redirect to corresponding detail page.
- If paper was not saved: favourite is created.
- If paper was already saved for user and `(source, external_paper_id)`: favourite is removed.

### Data Guarantees

- Duplicate rows for same `(user_id, source, external_paper_id)` MUST NOT be created.
- Save/remove effects are scoped to current authenticated user only.

## Route: GET /favourites

Displays favourites list for current authenticated user.

### Auth Behavior

- Authenticated: returns `200` with favourites page.
- Unauthenticated: returns generic not-found (`404`).

### Render Guarantees

- List contains only favourites owned by current user.
- List ordering is descending by `created_at` (most recently added first).
- Empty list renders clear "No favourites saved yet" state.

## Route: POST /favourite/remove

Removes one favourite for current authenticated user.

### Request

Form fields:
- `item_id` (required): external paper identifier to remove
- `source` (required or defaulted): source discriminator used with `item_id`

### Auth Behavior

- Authenticated: remove if matching favourite exists for current user.
- Unauthenticated: returns generic not-found (`404`).

### Success Response

- Status: `302`/`303` redirect to `/favourites`.
- Removing non-existent item is idempotent and does not error.

## Template/Navigation Contract

- Global navigation MUST hide favourites entry for unauthenticated users.
- Authenticated users MUST see favourites navigation entry consistently.

## Persistence Contract

- Favourites are persisted in database and remain available across login sessions for same user.
- User account deletion MUST immediately remove all owned favourites.

## Compatibility Constraints

- Existing discovery and detail routes remain stable.
- Feature introduces no new public API versioning path; behavior evolves in-place for existing routes.

## Implementation Ownership Notes

- Auth gating and route-level 404 behavior are enforced in `src/app.py`.
- Ownership and duplicate-prevention constraints are enforced in `src/services/db.py`.
- Navigation visibility behavior is enforced in `src/templates/base.html`.
