# API Contract: User Email Registration

**Feature**: 002-user-email-registration  
**Phase**: 1 — Design  
**Date**: 2026-05-14

## Purpose

Define the HTTP interface exposed by the registration feature: form submission, email verification, and resend endpoints. All endpoints are rendered as HTML pages (server-side Flask templates) except where JSON is noted.

---

## Endpoints

### GET /register

Display the registration form.

**Response**: HTML registration page containing:
- Email field (type=`email`)
- Password field (type=`password`)
- Consent checkbox linking to Privacy Policy page (FR-013)
- Submit button

**Status codes**:
- `200 OK` — form rendered

---

### POST /register

Submit the registration form.

**Request body** (application/x-www-form-urlencoded):

| Field | Required | Description |
|---|---|---|
| `email` | Yes | Email address (must end with `@gmail.com`) |
| `password` | Yes | Plaintext password (min 8 chars, ≥1 letter, ≥1 digit) |
| `consent` | Yes | Must be `"on"` (checkbox checked) |

**Success flow** (all validation passes, account created, email sent):
- Status: `302 Redirect` → `GET /check-email`
- Side effect: `UserAccount` created with `status='pending'`; `VerificationToken` created; verification email sent; Flask session populated with `registration_id`, `masked_email`, `next_resend_allowed_at`

**Validation failure** (field-level errors):
- Status: `200 OK` — re-renders registration form with field-level error messages; previously entered valid fields preserved (FR-009)

**Error cases**:

| Scenario | HTTP Status | Behaviour |
|---|---|---|
| Email domain not `@gmail.com` | 200 | Field error: "Only Gmail addresses are supported." |
| Email already registered (any status) | 200 | Field error: "This email is already registered. [Sign in]" — no disclosure of account status (FR-010) |
| Password too short or missing digit/letter | 200 | Field error: "Password must be at least 8 characters and include a letter and a digit." |
| Consent checkbox unchecked | 200 | Checkbox error: "You must accept the Privacy Policy to register." |

---

### GET /check-email

Display the "Check your email" confirmation page (FR-014).

**Prerequisites**: Valid Flask session set by `POST /register`; redirects to `/register` if session absent.

**Response**: HTML page containing:
- Masked email address (e.g., `g***@gmail.com`) from session
- Instruction to check inbox and click verification link
- Resend verification email form (POST to `/resend-verification`)
- Resend link disabled / countdown shown if `next_resend_allowed_at` in future

**Status codes**:
- `200 OK` — page rendered
- `302 Redirect` → `/register` if no valid session

---

### POST /resend-verification

Request a new verification email.

**Prerequisites**: Valid Flask session from `POST /register` (same session).

**Request body** (application/x-www-form-urlencoded): *(no fields required; registration_id taken from session)*

**Success** (resend allowed — within limits and past cooldown):
- Status: `302 Redirect` → `GET /check-email`
- Side effect: `VerificationToken.resend_count` incremented; new `token_value` and `expires_at` set; new email sent; session `next_resend_allowed_at` updated

**Error cases**:

| Scenario | HTTP Status | Behaviour |
|---|---|---|
| 60-second cooldown not elapsed | 200 | `/check-email` re-rendered with countdown message |
| `resend_count` already at 3 | 200 | `/check-email` re-rendered with message: "Maximum resend attempts reached. Please re-register." |
| Session missing or expired | 302 | Redirect to `/register` |
| Account already active (verified) | 302 | Redirect to `/register` with message: "Your account is already verified." |

---

### GET /verify/\<token\>

Consume a verification link from email.

**Path parameter**:
- `token` — URL-safe token string (value of `VerificationToken.token_value`)

**Success** (token valid, not expired, not already used):
- Status: `200 OK` — renders confirmation page ("Your email has been verified!")
- Side effect: `UserAccount.status` set to `'active'`; `UserAccount.verified_at` set; `VerificationToken.used_at` set

**Error cases**:

| Scenario | HTTP Status | Behaviour |
|---|---|---|
| Token not found | 404 | Error page: "Verification link not found or already used." |
| Token expired (`expires_at` < NOW) | 200 | Expiry page with resend option (FR-007; US2 scenario 2) — redirects to `/check-email` if session present, else shows standalone resend form |
| Token already used (`used_at` not null) | 200 | Friendly page: "Your email is already verified." (US2 scenario 3) |

---

## Notes

- All form POSTs use `application/x-www-form-urlencoded` (standard HTML form encoding).
- CSRF protection MUST be applied to all POST endpoints (standard Flask-WTF or equivalent).
- SMTP failures on verification email send do not block account creation; error is recorded to `EmailNotification.delivery_status='failed'` and the user lands on `/check-email` with an option to resend.
- The `SECRET_KEY` Flask configuration MUST be set to a cryptographically random value in production for session signing security.
- Pending account purge (`_purge_expired_pending_accounts()`) is invoked as a silent side effect at the start of `POST /register` and `GET /verify/<token>` handlers.
