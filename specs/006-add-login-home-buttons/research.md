# Research: Add Login and Home Button

**Feature**: `006-add-login-home-buttons`
**Date**: 2026-05-26

---

## 1. Password Verification

**Decision**: Use `werkzeug.security.check_password_hash(user.password_hash, submitted_password)`.

**Rationale**: Registration already uses `werkzeug.security.generate_password_hash`. Using the matching `check_password_hash` function keeps the dependency footprint zero (Werkzeug is already a Flask transitive dependency) and ensures hash algorithm compatibility.

**Alternatives considered**: `bcrypt` directly, `passlib` — both rejected because Werkzeug's implementation already owns the stored hash format; switching would invalidate all existing password hashes.

---

## 2. Session Key for Login State

**Decision**: Store `session["user_id"] = user.id` (integer) on successful login. Clear it with `session.pop("user_id", None)` on logout.

**Rationale**: The existing session already uses integer keys (`session["registration_id"]`). Storing the primary key is the minimal, idiomatic Flask pattern — no token table needed. The `user_id` is sufficient to check auth state and to look up the user if needed later.

**Alternatives considered**:
- Flask-Login — rejected: adds a new dependency; overkill for a single session key
- Storing full user dict in session — rejected: duplicates DB data; stale if account changes

---

## 3. Auth State Check in Templates (Jinja2)

**Decision**: Pass `logged_in = "user_id" in session` as a template variable from every route that renders a page. The `base.html` nav uses `{% if logged_in %}` to switch between "Login" link and "Log out" button.

**Rationale**: Flask's `session` proxy is available in Jinja2 via `{{ session }}` but reading it directly in templates couples the template to implementation. Passing an explicit `logged_in` boolean is cleaner, testable, and consistent with the project's existing context-passing pattern (see `app.py` home/register routes).

**Alternative considered**: Use a `@app.context_processor` to inject `logged_in` globally — valid approach, but adds a global side effect. Explicit passing is simpler and consistent with the existing codebase style.

---

## 4. CSRF Protection for POST /logout

**Decision**: Implement logout as `POST /logout` with no CSRF token for now — the app has no CSRF protection anywhere (including `POST /register`), so adding it only for logout would be inconsistent. Document as a known gap to address in a future security hardening feature.

**Rationale**: The existing `POST /register` and `POST /resend-verification` routes carry no CSRF token. Introducing CSRF only for logout is inconsistent and would require adding Flask-WTF or a custom token mechanism — out of scope for this feature.

**Risk**: Low — logout CSRF is a nuisance attack (forces logout), not a data-exfiltration risk. No session tokens are elevated by forcing logout.

---

## 5. Home Button Placement

**Decision**: Add `<a href="/">Home</a>` as the first item in the existing `.nav-dropdown__list` `<ul>` in `base.html`. This is inside the existing hamburger dropdown — consistent with how "Register" is currently placed.

**Rationale**: The existing nav pattern puts all nav items in the hamburger dropdown (`#menu-dropdown`). Placing "Home" there is zero-friction and consistent. A persistent always-visible "Home" link above/outside the dropdown would require CSS changes beyond the feature scope.

**Alternative considered**: A persistent "Home" link always visible (outside dropdown) — deferred. The spec says "visible Home link on every page" and the hamburger is the current nav structure; the dropdown is always accessible.

---

## 6. Login Service Layer Placement

**Decision**: Add a `login_user(email, password)` function to `src/services/registration_service.py` (rename to `auth_service.py` is explicitly out of scope — the file already has a mixed name for the registered feature). Alternatively, create a new `src/services/login_service.py`.

**Decision (final)**: Create `src/services/login_service.py` as a thin, focused module. Adding login logic to `registration_service.py` would violate single-responsibility — registration and authentication are distinct concerns.

**Rationale**: Registration service is already 150+ lines; it handles registration, verification, and resend. Adding login/logout would couple distinct auth stages into one module. A dedicated `login_service.py` keeps both modules focused.

---

## 7. Login Template

**Decision**: Create `src/templates/login.html` extending `base.html`, with an email field, password field, and submit button — consistent with `register.html` form pattern.

**Rationale**: The existing `register.html` template provides the form layout pattern to follow. No new CSS classes needed if we reuse existing `.form-group`, `.error-message` etc.

---

## 8. Test Coverage

**Existing test count**: 48 (after feature 005).

**New tests needed**:
- `tests/unit/test_login_service.py`: unit tests for `login_user()` — valid credentials, wrong password, non-existent email, pending account
- `tests/integration/test_login_flow.py`: integration tests covering the full login/logout flow, redirect behavior, nav state

**Expected final test count**: 48 + ~8 new = ~56 tests.
