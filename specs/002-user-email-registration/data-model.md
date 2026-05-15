# Data Model: User Email Registration

**Feature**: 002-user-email-registration  
**Phase**: 1 — Design  
**Date**: 2026-05-14  
**Storage**: SQLite via Flask-SQLAlchemy

---

## Entities

### UserAccount

Represents a registered site user.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO INCREMENT | Internal surrogate key |
| `email` | VARCHAR(254) | UNIQUE NOT NULL | Gmail addresses only (`@gmail.com`). Stored lowercase. |
| `password_hash` | VARCHAR(256) | NOT NULL | One-way hash via `werkzeug.security`. Plaintext never stored. |
| `status` | VARCHAR(16) | NOT NULL, DEFAULT `'pending'` | Enum: `'pending'` or `'active'` |
| `created_at` | DATETIME | NOT NULL, DEFAULT UTC NOW | Registration timestamp |
| `verified_at` | DATETIME | NULLABLE | Set when account transitions to `'active'` |
| `consent_at` | DATETIME | NOT NULL | Timestamp of Privacy Policy checkbox acceptance |

**Lifecycle**:
- Created with `status='pending'` on successful form submission (FR-001, FR-005).
- Transitions to `status='active'` when the user clicks a valid verification link (FR-006).
- Purged (deleted) if `status='pending'` and `created_at < NOW() - 24h` (FR-011). Email address becomes available for re-registration after purge.

**Validation rules**:
- `email` must end with `@gmail.com` (FR-002).
- `email` must be unique across all accounts regardless of status (FR-004 / FR-010).
- `password_hash` stored as output of `werkzeug.security.generate_password_hash()` (FR-015).
- `consent_at` must be set at account creation time (FR-012).

---

### VerificationToken

A single-use token linking a pending `UserAccount` to an email verification link.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO INCREMENT | Internal surrogate key |
| `user_id` | INTEGER | FK → UserAccount.id, NOT NULL, ON DELETE CASCADE | Owning account |
| `token_value` | VARCHAR(64) | UNIQUE NOT NULL, INDEXED | Generated via `secrets.token_urlsafe(32)` (256-bit entropy) |
| `created_at` | DATETIME | NOT NULL, DEFAULT UTC NOW | Token issuance timestamp |
| `expires_at` | DATETIME | NOT NULL | `created_at + 24h` (FR-007) |
| `used_at` | DATETIME | NULLABLE | Set when token is consumed; non-null means already used |
| `resend_count` | INTEGER | NOT NULL, DEFAULT 0 | Number of resend requests issued (max 3, FR-008) |

**Lifecycle**:
- One token per `UserAccount` at any time. Created alongside the `UserAccount` on registration.
- Marked `used_at = NOW()` when the user follows the verification link and account is activated.
- Resend request: `resend_count` incremented, new `token_value` and `expires_at` generated in-place (replaces old token), new email sent.
- Cascade-deleted when parent `UserAccount` is deleted (purge or future account management).

**Validation rules**:
- `resend_count` MUST NOT exceed 3 (FR-008). Attempt beyond limit returns error with guidance to re-register.
- `expires_at` MUST be checked before activating account (FR-007).
- `used_at` MUST be checked before activating account (idempotency — already-used link returns friendly message, US2 scenario 3).
- `token_value` MUST be indexed for fast lookup during verification link handling.

---

### EmailNotification *(records only — best-effort)*

An append-only log of outbound email attempts. Does not affect application flow on failure (best-effort delivery per spec assumption).

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO INCREMENT | Internal surrogate key |
| `user_id` | INTEGER | FK → UserAccount.id, NULLABLE, ON DELETE SET NULL | May be NULL if account is later purged |
| `recipient_email` | VARCHAR(254) | NOT NULL | Destination address (copy stored for audit purposes) |
| `message_type` | VARCHAR(32) | NOT NULL | `'verification'` or `'resend_verification'` |
| `sent_at` | DATETIME | NOT NULL, DEFAULT UTC NOW | Timestamp of send attempt |
| `delivery_status` | VARCHAR(16) | NOT NULL, DEFAULT `'sent'` | `'sent'` or `'failed'` (updated if SMTP raises) |

**Notes**:
- Read by no application flow (informational only for admin inspection or future observability feature).
- Not surfaced to the user. Delivery failures noted but do not block user flow.

---

## Entity Relationships

```
UserAccount 1──────────────────── 1 VerificationToken
            (UserAccount.id = VerificationToken.user_id)
            (CASCADE DELETE)

UserAccount 1──────────────────── * EmailNotification
            (UserAccount.id = EmailNotification.user_id)
            (SET NULL on account delete)
```

---

## State Transitions

### UserAccount.status

```
[new registration]
      │
      ▼
  'pending' ──── verification link clicked (valid, unexpired) ──▶ 'active'
      │
      └──── created_at + 24h, status still 'pending' ──▶ [PURGED / deleted]
```

### VerificationToken.resend_count

```
0 ──resend──▶ 1 ──resend──▶ 2 ──resend──▶ 3 (limit reached)
                                               │
                                               └──▶ error: must re-register
```

---

## Indexes

| Table | Column(s) | Purpose |
|---|---|---|
| `UserAccount` | `email` | Fast duplicate-check on registration (FR-004) |
| `VerificationToken` | `token_value` | Fast lookup on verification link click |
| `VerificationToken` | `user_id` | Fast lookup for resend requests |
| `UserAccount` | `status`, `created_at` | Fast purge query (`WHERE status='pending' AND created_at < ?`) |
