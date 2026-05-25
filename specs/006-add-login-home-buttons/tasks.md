# Tasks: Add Login and Home Button

**Input**: Design documents from `specs/006-add-login-home-buttons/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓
**Branch**: `006-add-login-home-buttons`

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[US1]** / **[US2]**: Which user story this task belongs to
- Exact file paths included in every task description

---

## Phase 1: Setup

**Purpose**: Verify the baseline is green before any source files are touched.

- [X] T001 Verify existing test suite passes with `python -m pytest tests/ -v` (expected: 48 tests passing)

**Checkpoint**: All 48 existing tests green — safe to begin.

---

## Phase 2: Foundational (Blocking Prerequisite)

**Purpose**: Create the credential-verification function that both the login route (app.py) and the unit tests depend on. Must exist before any US1 implementation begins.

- [X] T002 Create `src/services/login_service.py` — add `login_user(email: str, password: str)` function that: (1) imports `check_password_hash` from `werkzeug.security` and `UserAccount` from `src.models.user`; (2) looks up `UserAccount.query.filter_by(email=email.strip().lower()).first()`; (3) returns `(user.id, None)` only if user exists AND `user.status == "active"` AND `check_password_hash(user.password_hash, password)` is True; (4) returns `(None, "Invalid email or password.")` for ALL other cases (not found, wrong password, pending account)

**Checkpoint**: `python -m pytest tests/unit/ -v` — all existing unit tests still pass; `login_service.py` importable.

---

## Phase 3: User Story 1 — Registered User Logs In (Priority: P1) 🎯 MVP

**Goal**: A verified user can log in at `/login`, see a "Log out" button in the nav, and log out. Wrong credentials show a generic error. Authenticated users visiting `/login` or `/register` are redirected to home.

**Independent Test**: `GET /login` → 200; `POST /login` with valid credentials → 302 to `/`, session contains `user_id`; `POST /login` with wrong password → 200 with generic error, email pre-filled; `POST /logout` → 302 to `/`, session cleared; `GET /login` while logged in → 302 to `/`; `GET /register` while logged in → 302 to `/`; nav shows "Log out" when `logged_in=True`.

### Implementation for User Story 1

- [X] T003 [P] [US1] Create `tests/unit/test_login_service.py` with 4 unit tests — all mock `UserAccount.query.filter_by`: (1) `test_login_valid_credentials` → assert returns `(user.id, None)`; (2) `test_login_wrong_password` → assert returns `(None, "Invalid email or password.")`; (3) `test_login_email_not_found` → assert returns `(None, "Invalid email or password.")`; (4) `test_login_pending_account` → assert returns `(None, "Invalid email or password.")`
- [X] T004 [P] [US1] Create `src/templates/login.html` extending `base.html` — `{% block content %}` with a `<form method="post" action="/login">` containing: email `<input type="email" name="email" value="{{ form_email }}">`, password `<input type="password" name="password">`, submit button; above the form render `{% if error %}<p class="error-message">{{ error }}</p>{% endif %}`
- [X] T005 [P] [US1] In `src/app.py`: (1) import `login_user` from `src.services.login_service`; (2) add `@app.route("/login", methods=["GET", "POST"])` — GET: if `"user_id" in session` redirect to `/`, else render `login.html` with `error=None, form_email="", logged_in=False`; POST: call `login_user(email, password)`, on success set `session["user_id"] = user_id` and redirect to `/`, on failure re-render `login.html` with `error=msg, form_email=email, logged_in=False`; (3) add `@app.route("/logout", methods=["POST"])` — `session.pop("user_id", None)` then redirect to `/`; (4) add `logged_in = "user_id" in session` to the template context dict in `home()`, `item_detail()`, `check_email()`, and `register()` (render_template calls); (5) add auth guard to `register()` GET handler: if `"user_id" in session` return `redirect(url_for("home"))`
- [X] T006 [US1] In `src/templates/base.html` — in the `<ul class="nav-dropdown__list">`: replace the existing `<li>` content with a Jinja2 conditional block — `{% if logged_in %}` renders a `<li class="nav-dropdown__item"><form method="post" action="/logout"><button type="submit" class="nav-logout-btn">Log out</button></form></li>`; `{% else %}` renders the existing `<li class="nav-dropdown__item"><a href="/register">Register</a></li>` plus a new `<li class="nav-dropdown__item"><a href="/login">Login</a></li>`; depends on T005 (logged_in passed from routes)
- [X] T007 [US1] Create `tests/integration/test_login_flow.py` with 7 integration tests using `app.test_client()` and `app.app_context()`: (1) `test_get_login_page` → GET `/login` returns 200 with `<form`; (2) `test_post_login_valid_credentials` → mock `login_user` returning `(1, None)`, POST `/login` → 302 to `/`, assert `session["user_id"] == 1`; (3) `test_post_login_invalid_credentials` → mock `login_user` returning `(None, "Invalid email or password.")`, POST `/login` → 200 with `b"Invalid email or password."`; (4) `test_post_logout` → set session `user_id=1`, POST `/logout` → 302 to `/`, assert `"user_id" not in session`; (5) `test_login_redirects_when_authenticated` → set session `user_id=1`, GET `/login` → 302 to `/`; (6) `test_register_redirects_when_authenticated` → set session `user_id=1`, GET `/register` → 302 to `/`; (7) `test_nav_shows_logout_when_logged_in` → set session `user_id=1`, GET `/` → 200, assert `b"Log out"` in response; depends on T004, T005, T006

**Checkpoint**: `python -m pytest tests/unit/test_login_service.py tests/integration/test_login_flow.py -v` — all 11 new tests pass; manual AC-2 through AC-7 from quickstart.md pass.

---

## Phase 4: User Story 2 — Home Button Visible on Every Page (Priority: P2)

**Goal**: A "Home" link is the first item in the nav dropdown on every page, visible to both authenticated and unauthenticated users.

**Independent Test**: GET `/register`, `/check-email`, `/detail/<any-id>` — each response contains a "Home" `<a>` link pointing to `/`. The link is present regardless of login state.

### Implementation for User Story 2

- [X] T008 [US2] In `src/templates/base.html` — in the `<ul class="nav-dropdown__list">`, insert `<li class="nav-dropdown__item"><a href="/">Home</a></li>` as the very first `<li>`, before the `{% if logged_in %}` conditional block added in T006; this item is outside the conditional so it renders for all users; depends on T006 (same file — apply after T006 is complete)

**Checkpoint**: GET any page → nav dropdown contains "Home" link. Manual AC-1 from quickstart.md passes.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final regression guard and manual acceptance test validation.

- [X] T009 [P] Run full test suite `python -m pytest tests/ -v` and confirm ~56 tests pass (48 existing + 4 unit + ~7 integration = ~59, adjust based on actual count)
- [X] T010 [P] Run quickstart manual acceptance tests AC-1 through AC-7 from `specs/006-add-login-home-buttons/quickstart.md` against `python -m flask --app src.app run --debug`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 checkpoint — T002 must complete before any Phase 3 work
- **Phase 3 (US1)**: T003, T004, T005 all depend on T002; can run in parallel with each other; T006 depends on T005; T007 depends on T004 + T005 + T006
- **Phase 4 (US2)**: T008 depends on T006 (same file `base.html`)
- **Phase 5 (Polish)**: Depends on Phase 4

### Within Phase 3

- **T003** (`tests/unit/test_login_service.py`), **T004** (`src/templates/login.html`), **T005** (`src/app.py`) → **[P]** all edit different files, all depend only on T002
- **T006** (`src/templates/base.html`) → depends on T005 (needs `logged_in` from routes)
- **T007** (`tests/integration/test_login_flow.py`) → depends on T004 + T005 + T006 (tests full flow)

### Parallel Opportunities

```text
# Phase 2 (sequential only):
T002  src/services/login_service.py  (create login_user function)

# Phase 3 (parallel start, sequential finish):
[P] T003  tests/unit/test_login_service.py     (unit tests)
[P] T004  src/templates/login.html             (login form template)
[P] T005  src/app.py                           (routes + context + guards)
    T006  src/templates/base.html              (Login/Logout conditional — after T005)
    T007  tests/integration/test_login_flow.py (integration tests — after T004+T005+T006)

# Phase 4 (single task):
    T008  src/templates/base.html              (Home link — after T006)

# Phase 5 (parallel):
[P] T009  pytest full suite
[P] T010  manual quickstart ACs
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

Implementing Phase 1 + Phase 2 + Phase 3 alone delivers a fully working login/logout flow with all acceptance criteria met. User Story 2 (Home link) is additive — the app is usable without it, but it fixes the existing navigation gap.

### Suggested Execution Order (single implementer)

```
T001 → T002 → T005 → T006 → T008 → T004 → T003 → T007 → T009 → T010
```

This keeps `base.html` edits grouped (T006 immediately followed by T008) and ensures `app.py` exists before writing integration tests.
