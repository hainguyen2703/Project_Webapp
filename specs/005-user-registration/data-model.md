# Data Model: User Registration

**Feature**: 005-user-registration  
**Date**: 2026-06-02

## Entity: UserAccount

Represents a registered account that can authenticate in later flows.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Internal account identifier |
| `email` | TEXT | NOT NULL, UNIQUE | Stored exactly as submitted after validation; leading/trailing whitespace is rejected before insert |
| `password_hash` | TEXT | NOT NULL | Generated with Werkzeug `generate_password_hash` |
| `is_active` | INTEGER | NOT NULL DEFAULT 1 | Accounts are active immediately after successful registration |
| `created_at` | TEXT | NOT NULL | ISO-8601 UTC timestamp |
| `updated_at` | TEXT | NOT NULL | ISO-8601 UTC timestamp |

### Validation rules

- Email is required.
- Email must not start or end with whitespace.
- Email must be unique across all accounts.
- Password is required.
- Password must be at least 8 characters and include at least one letter and one number.

## Entity: RegistrationAttempt (transient)

Represents one registration submission in request processing. This is not persisted as a database table in this feature scope.

| Field | Type | Purpose |
|-------|------|---------|
| `submission_token` | TEXT | Detect duplicate in-flight submissions |
| `email` | TEXT | Candidate identity |
| `validation_errors` | list[str] | User-facing failure reasons |
| `result` | ENUM | `success`, `validation_error`, `duplicate_email`, `duplicate_submission` |
| `processed_at` | TEXT | Request completion timestamp |

## Relationships

- One `UserAccount` can be created by many `RegistrationAttempt` events over time, but only one attempt can succeed for a unique email.

## State transitions

1. `submitted` -> `validation_error` when required fields/policy/whitespace checks fail.
2. `submitted` -> `duplicate_submission` when the token is already in-flight.
3. `submitted` -> `duplicate_email` when email already exists.
4. `submitted` -> `success` when validation passes and insert commits.

## Invariants

- No two `UserAccount` rows share the same email.
- Password values are never persisted in plaintext.
- New accounts are active (`is_active = 1`) immediately after successful insert.
