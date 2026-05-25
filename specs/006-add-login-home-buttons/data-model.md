# Data Model: Add Login and Home Button

**Feature**: `006-add-login-home-buttons`
**Date**: 2026-05-26

---

## 1. Changed Entities

### No schema changes

No new database tables or columns are introduced. The feature uses the existing `UserAccount` model entirely as-is.

---

## 2. Existing Entities Used

### UserAccount (read-only usage)

| Field | Type | Used By |
|-------|------|---------|
| `id` | Integer (PK) | Stored in `session["user_id"]` on login |
| `email` | String(254) | Matched against submitted login email |
| `password_hash` | String(256) | Verified via `check_password_hash` |
| `status` | String(16) | Must equal `"active"` to allow login |

**Access pattern**: `UserAccount.query.filter_by(email=email.strip().lower()).first()`  
**Status gate**: Only accounts with `status == "active"` produce a successful login. Accounts with `status == "pending"` are treated as invalid credentials (FR-006).

---

## 3. Session State

### Flask Session Keys (additions)

| Key | Type | Set When | Cleared When |
|-----|------|----------|--------------|
| `user_id` | Integer | `POST /login` succeeds | `POST /logout` |

**Existing session keys** (`registration_id`, `masked_email`, `next_resend_allowed_at`) are unaffected — they are set during registration flow and not read by login/logout.

**Auth state check**: `"user_id" in session` → `True` means authenticated.

---

## 4. State Transitions

```
Unauthenticated
    │
    │  POST /login (valid credentials, status=active)
    ▼
Authenticated  ──── session["user_id"] = user.id
    │
    │  POST /logout
    ▼
Unauthenticated  ──── session.pop("user_id")
```

---

## 5. Validation Rules

| Rule | Condition | Response |
|------|-----------|----------|
| Email format | Must be non-blank | Generic error (FR-005) |
| Account lookup | `UserAccount` with matching email must exist | Generic error (FR-005) |
| Status check | `user.status == "active"` | If pending/other: generic error (FR-006) |
| Password check | `check_password_hash(user.password_hash, password)` returns True | If False: generic error (FR-005) |

**Security rule**: The same generic error message MUST be shown for all failure cases (non-existent email, wrong password, pending account) to prevent user enumeration (FR-005).
