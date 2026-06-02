# API Contract: User Registration (v1)

**Feature**: 005-user-registration  
**Date**: 2026-06-02

## New Endpoints

### GET /register

Render the registration page.

**Request**: no body

**Response**:

| Condition | Status | Behavior |
|-----------|--------|----------|
| Any visitor state (signed in or signed out) | 200 | Render registration form |

### POST /register

Submit registration data.

**Content-Type**: `application/x-www-form-urlencoded`

**Request fields**:

| Field | Required | Rules |
|-------|----------|-------|
| `email` | Yes | Must be present, unique, and must not include leading/trailing whitespace |
| `password` | Yes | Minimum 8 chars, at least 1 letter and 1 number |
| `submission_token` | Yes | Used to detect in-flight duplicate submissions |

**Behavior**:

| Condition | Status | Response |
|-----------|--------|----------|
| Valid input, unique email, first in-flight submission | 303 | Redirect to `GET /?registered=1` with success flash/message |
| Validation failure (missing fields, password policy, whitespace email) | 200 | Re-render `register.html` with field-level errors |
| Duplicate email | 200 | Re-render `register.html` with duplicate-email error |
| Duplicate in-flight submission token | 409 or 200 | Return duplicate-submission error view/message; no second account creation |

## Security Contract

- Passwords MUST be hashed using Werkzeug before persistence.
- Password plaintext MUST never be logged or stored.
- Error responses MUST not expose internal stack traces or SQL details.

## Data Contract

Successful registration creates one `UserAccount` row with:
- unique `email`
- hashed `password_hash`
- `is_active = 1`
- `created_at` and `updated_at` timestamps

## Compatibility

- Existing endpoints remain backward compatible (`/`, `/api/listings`, `/detail/<item_id>`, favourites routes).
- Registration flow adds new route surface without changing existing response formats.
