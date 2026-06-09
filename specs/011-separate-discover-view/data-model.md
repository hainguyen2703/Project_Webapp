# Data Model: Separate Discover View

**Feature**: 011-separate-discover-view  
**Date**: 2026-06-09

## Entity: ViewContext

Current user-facing page identity and active navigation state.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `route` | enum(`home`,`discover`) | Required | Maps to `/` and `/discover` |
| `is_active` | boolean | Required | Used for active nav indicator rendering |
| `user_id` | integer or null | Optional | Present when authenticated context is available |

## Entity: DiscoverSessionState

Session-scoped state shared between Home and Discover for parity behavior.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `query` | string | Optional | Last in-session query value synced across `/` and `/discover` |
| `filters` | map[string,string] | Optional | Session-scoped filter selections |
| `used_default_interest_query` | boolean | Required | Indicates default-personalized mode |
| `backfill_applied` | boolean | Required | Indicates sparse-result backfill state |
| `last_updated_at` | string (ISO-8601) | Required | Session traceability |

## Entity: RouteAccessPolicy

Route-level access and redirect behavior.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `route` | string | Required | `/` or `/discover` |
| `requires_auth` | boolean | Required | `/discover` true, `/` false |
| `redirect_target` | string | Optional | For unauthenticated `/discover`, target is `/login` |
| `post_login_target` | string | Required | Home route (`/`) |

## Relationships

- One authenticated user can have one active `DiscoverSessionState` per browser session.
- `ViewContext` uses `RouteAccessPolicy` to determine entry and redirect behavior.
- `DiscoverSessionState` feeds both Home and Discover rendering when discovery behavior is invoked.

## Validation Rules

- Accessing `/discover` while unauthenticated must redirect to login.
- Successful login lands on `/`.
- Query/filter synchronization between `/` and `/discover` is session-only and does not rely on URL parameters.
- Discovery search controls and result rendering behavior must remain functionally identical across `/` and `/discover`.
- Existing personalized discovery prerequisites remain enforced for authenticated Discover access.

## State Transitions

1. `Unauthenticated` -> `LoginRedirected` when `/discover` is requested.
2. `Authenticated` -> `HomeActive` immediately after successful login.
3. `HomeActive` <-> `DiscoverActive` via user navigation while preserving session-scoped discovery state.
4. `SessionActive` -> `SessionExpired` clears synchronized Home/Discover state.

## Integrity Considerations

- Session data must be scoped per browser session and must not leak across users.
- Route identity and active nav state must remain deterministic and mutually exclusive per rendered view.
