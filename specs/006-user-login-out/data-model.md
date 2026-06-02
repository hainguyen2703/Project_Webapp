# Data Model: User Login and Logout

**Feature**: 006-user-login-out  
**Date**: 2026-06-03

## Entity: AuthenticatedSession

Represents the active authentication state for a user session.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `session_id` | TEXT | Required | Unique runtime session key |
| `user_id` | INTEGER | Required | References existing `user_accounts.id` |
| `issued_at` | TEXT | Required | ISO-8601 timestamp |
| `expires_at` | TEXT | Required | ISO-8601 timestamp |
| `is_active` | BOOLEAN | Required | Deactivated on logout or global invalidation |
| `version` | INTEGER | Required | Supports cross-device invalidation token checks |

## Entity: LoginAttempt

Tracks login submissions for validation and throttling logic.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `attempt_id` | TEXT | Required | Internal tracking identifier |
| `email` | TEXT | Required | Submitted identity |
| `occurred_at` | TEXT | Required | Attempt timestamp |
| `outcome` | ENUM | Required | `success`, `invalid_credentials`, `throttled`, `blocked` |
| `throttle_until` | TEXT | Optional | Present only when throttled |

## Entity: AuthUser (adapter)

Runtime adapter object consumed by Flask-LoginManager.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | str | Required | Flask-Login user identifier |
| `email` | str | Required | Display/lookup identity |
| `is_authenticated` | bool | Required | Derived from active login state |
| `session_version` | int | Required | Compared against latest version for global logout invalidation |

## Relationships

- One account (`user_accounts`) can own many `AuthenticatedSession` records over time.
- One account can have many `LoginAttempt` events.
- `AuthUser` is a runtime projection over persisted account/session state.

## State Transitions

1. `LoginAttempt` submitted -> `invalid_credentials` when email/password check fails.
2. `LoginAttempt` submitted -> `throttled` when rapid failure threshold reached.
3. `LoginAttempt` submitted -> `success` when credentials verify and session is activated.
4. `AuthenticatedSession` active -> inactive on explicit logout.
5. User global logout invalidates all active sessions by version bump/invalidation flag.
6. Expired `AuthenticatedSession` transitions to refreshed active session on next protected action per clarification.

## Invariants

- Failed login must never create an active authenticated session.
- Signed-out logout requests do not mutate active session state.
- Global logout invalidates all active sessions for the same user identity.
