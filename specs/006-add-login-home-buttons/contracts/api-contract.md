# API Contract: Add Login and Home Button

**Feature**: `006-add-login-home-buttons`
**Date**: 2026-05-26
**App type**: Flask server-rendered web application (Jinja2 templates)

---

## New Routes

### GET /login

Returns the login form page.

**Auth guard**: If `"user_id" in session` → redirect 302 to `GET /` (FR-007).

**Response (unauthenticated)**:
- Status: `200 OK`
- Body: HTML — `login.html` rendered with `{error: None, form_email: ""}`

---

### POST /login

Processes login form submission.

**Auth guard**: If `"user_id" in session` → redirect 302 to `GET /` (FR-007).

**Request body** (application/x-www-form-urlencoded):

| Field | Type | Required |
|-------|------|----------|
| `email` | string | yes |
| `password` | string | yes |

**Response — success**:
- Condition: Account found, `status == "active"`, password matches
- Action: `session["user_id"] = user.id`
- Status: `302` redirect to `GET /`

**Response — failure**:
- Condition: Any of — email not found, password wrong, `status != "active"`
- Status: `200 OK` (re-render form, not 401)
- Body: HTML — `login.html` rendered with `{error: "Invalid email or password.", form_email: <submitted_email>}`
- Security: Same error message for all failure cases (FR-005)

---

### POST /logout

Destroys the user session.

**Request body**: empty (no fields required)

**Response**:
- Action: `session.pop("user_id", None)`
- Status: `302` redirect to `GET /`

**Note**: Accessible to both authenticated and unauthenticated users — calling logout when not logged in is a no-op redirect.

---

## Modified Routes

### GET / (home)

**Change**: `logged_in = "user_id" in session` added to template context.

**Contract change**: No URL or parameter changes.

### GET /detail/\<item_id\>

**Change**: `logged_in = "user_id" in session` added to template context.

**Contract change**: No URL or parameter changes.

### GET /register

**Change**: Auth guard added — if `"user_id" in session` → redirect 302 to `GET /` (FR-007).

**Contract change**: New redirect behavior for authenticated users only.

### All other page-rendering routes (check-email, verify, etc.)

**Change**: `logged_in = "user_id" in session` added to template context so nav renders correctly.

---

## Modified Templates

### base.html

**Change**: Nav dropdown gains two new conditional items:

```
Unauthenticated:  [Home] [Register] [Login]
Authenticated:    [Home] [Log out]
```

- "Home" link: always visible, `href="/"`
- "Register" link: visible only when `not logged_in`
- "Login" link: visible only when `not logged_in`, `href="/login"`
- "Log out" button (form `POST /logout`): visible only when `logged_in`

---

## Unchanged Routes

| Route | Method | Change |
|-------|--------|--------|
| `GET /api/listings` | GET | None |
| `GET /check-email` | GET | `logged_in` context added only |
| `POST /resend-verification` | POST | None |
| `GET /verify/<token>` | GET | None |
