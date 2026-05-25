# Quickstart: Add Login and Home Button

**Feature**: `006-add-login-home-buttons`
**Date**: 2026-05-26

---

## What This Feature Does

Adds a login page (`/login`) with email + password authentication, a logout route (`POST /logout`), and a "Home" link to every page's navigation. The nav dynamically shows "Login" / "Register" for unauthenticated users and a "Log out" button for authenticated users. Authenticated users who visit `/login` or `/register` are redirected to home.

---

## Files Changed

| File | Change |
|---|---|
| `src/services/login_service.py` | NEW: `login_user(email, password)` function |
| `src/app.py` | NEW: `GET/POST /login` and `POST /logout` routes; `logged_in` context added to all page routes; auth guard on `/register` |
| `src/templates/login.html` | NEW: login form page |
| `src/templates/base.html` | MODIFIED: Home link + conditional Login/Register/Log out nav items |
| `tests/unit/test_login_service.py` | NEW: unit tests for `login_service.login_user` |
| `tests/integration/test_login_flow.py` | NEW: integration tests for login, logout, and redirect flows |

---

## Running the App

```powershell
# From repo root
python -m flask --app src.app run --debug
```

Open `http://127.0.0.1:5000/` in a browser.

---

## Manual Acceptance Tests

### AC-1: Home link visible on every page (FR-001, SC-002)

1. Open `http://127.0.0.1:5000/`
2. Click the **☰ Menu** button
3. Confirm a **"Home"** link is visible in the dropdown
4. Navigate to `/register` — confirm "Home" is still visible in the dropdown
5. Navigate to `/check-email` (if accessible) — confirm "Home" is visible

### AC-2: Successful login redirects to home (FR-004, SC-001)

1. Ensure a verified (active) account exists via the registration flow
2. Open `http://127.0.0.1:5000/login`
3. Enter the registered email and password, click **Log in**
4. Confirm redirect to `http://127.0.0.1:5000/`
5. Open the nav dropdown — confirm **"Log out"** button is visible and **"Login" / "Register" are not**

### AC-3: Failed login shows generic error (FR-005, SC-003)

1. Open `http://127.0.0.1:5000/login`
2. Enter a valid email but wrong password, submit
3. Confirm an error message is shown (e.g., "Invalid email or password.")
4. Confirm the email field is pre-filled with the submitted email
5. Confirm the error message does **not** say "password is wrong" or "email not found"

### AC-4: Logout clears session (FR-009)

1. Log in (AC-2)
2. Open the nav dropdown, click **Log out**
3. Confirm redirect to home page
4. Open the nav dropdown — confirm **"Login"** and **"Register"** are visible again

### AC-5: Already-logged-in user visiting /login is redirected (FR-007)

1. Log in (AC-2)
2. Navigate to `http://127.0.0.1:5000/login`
3. Confirm immediate redirect to `http://127.0.0.1:5000/`

### AC-6: Already-logged-in user visiting /register is redirected (FR-007)

1. Log in (AC-2)
2. Navigate to `http://127.0.0.1:5000/register`
3. Confirm immediate redirect to `http://127.0.0.1:5000/`

### AC-7: Pending account cannot log in (FR-006)

1. Register a new account but do **not** verify the email
2. Attempt to log in with that account's credentials
3. Confirm the generic error message is shown (same as AC-3)

---

## Automated Tests

```powershell
# From repo root
python -m pytest tests/ -v
```

Expected: **~56 tests passing** (48 existing + ~8 new).
