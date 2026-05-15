# Tasks: UI Guest & Registration Navigation

**Input**: Design documents from `specs/003-ui-guest-registration-nav/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, quickstart.md ✓  
**Branch**: `003-ui-guest-registration-nav`

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[US1]** / **[US2]**: Which user story this task belongs to
- Exact file paths included in every task description

---

## Phase 1: Setup

**Purpose**: Confirm existing project baseline and test scaffold are ready before modifying any files.

- [X] T001 Verify existing test suite passes with `pytest tests/ -v` (expected: 38 tests passing)

**Checkpoint**: All 38 existing tests green — safe to begin implementing.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the CSS rules for the dropdown in `src/static/styles.css` before any template changes. CSS must exist before the template references the `.nav-dropdown` and `.nav-dropdown__list` class names that the HTML will use.

- [X] T002 Add `.nav-header` flex wrapper and `header { position: relative }` rule to `src/static/styles.css`
- [X] T003 Add `.nav-trigger` button reset and typography rules to `src/static/styles.css`
- [X] T004 Add `.nav-dropdown`, `.nav-dropdown.open`, and `.nav-dropdown__list` positioning rules to `src/static/styles.css`
- [X] T005 Add `.nav-dropdown__item` link hover/focus rules to `src/static/styles.css`

**Checkpoint**: CSS rules present — `base.html` template changes can now be applied.

---

## Phase 3: User Story 1 — Hamburger trigger visible on every page (Priority: P1) 🎯 MVP

**Goal**: Every page rendered by `base.html` shows the ☰ Menu trigger button in the header. No existing layout is shifted.

**Independent Test**: `GET /` returns HTML containing `id="menu-trigger"` and `aria-expanded="false"`. The existing `<h1>Paper Discovery</h1>` and subtitle `<p>` are still present in the same response.

### Implementation for User Story 1

- [X] T006 [US1] Wrap existing `<h1>` and `<p>` in a `.nav-header` flex `<div>` in `src/templates/base.html`
- [X] T007 [US1] Add `<button id="menu-trigger" class="nav-trigger" aria-label="Menu" aria-expanded="false" aria-controls="menu-dropdown">☰ Menu</button>` inside the flex wrapper in `src/templates/base.html`
- [X] T008 [US1] Add `<nav id="menu-dropdown" class="nav-dropdown" aria-label="Navigation">` with empty `<ul class="nav-dropdown__list">` immediately after the flex wrapper div in `src/templates/base.html`
- [X] T009 [US1] Add the vanilla JS IIFE toggle script as an inline `<script>` at the end of `<body>` in `src/templates/base.html`
- [X] T010 [US1] Write integration tests verifying trigger presence on `GET /` and `GET /register` in `tests/integration/test_nav_dropdown.py`

**Checkpoint**: `☰ Menu` button renders on every page; no layout shift; all 38 + new tests passing.

---

## Phase 4: User Story 2 — Register link inside the dropdown (Priority: P2)

**Goal**: Clicking the `☰ Menu` button opens a dropdown; the dropdown contains a "Register" link pointing to `/register`.

**Independent Test**: `GET /` returns HTML with `href="/register"` and text `Register` inside the `#menu-dropdown` nav element. `GET /register` also contains the trigger + dropdown (regression). The dropdown has no `.open` class on initial render.

### Implementation for User Story 2

- [X] T011 [US2] Add `<li><a href="/register">Register</a></li>` inside `<ul class="nav-dropdown__list">` in `src/templates/base.html`
- [X] T012 [US2] Extend `tests/integration/test_nav_dropdown.py` to assert: dropdown contains `href="/register"`, `Register` text, no `.open` class on initial render, and `aria-expanded="false"` on trigger

**Checkpoint**: `☰ Menu` → click → "Register" link visible; navigates to `/register`; dropdown hidden on initial page load.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, regression guard, and visual consistency check.

- [X] T013 [P] Run full test suite `pytest tests/ -v` and confirm all tests pass (38 pre-existing + new nav dropdown tests)
- [X] T014 [P] Manually run all 6 quickstart acceptance tests from `specs/003-ui-guest-registration-nav/quickstart.md` against `flask run --debug`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational CSS)**: Depends on Phase 1 checkpoint
- **Phase 3 (US1 — trigger)**: Depends on Phase 2 completion (CSS rules must exist before template change)
- **Phase 4 (US2 — register link)**: Depends on Phase 3 (trigger and dropdown `<nav>` must exist before adding items)
- **Phase 5 (Polish)**: Depends on Phase 4

### Within Each Phase

- **Phase 2**: T002–T005 all edit `styles.css` sequentially (same file)
- **Phase 3**: T006–T009 all edit `base.html` sequentially (same file); T010 (tests) can be written [P] alongside T006–T009 if desired since it targets a different file
- **Phase 4**: T011 edits `base.html`; T012 edits test file — can run in parallel [P] once T008 exists

### Parallel Opportunities

```text
# Phase 2 — sequential (same file):
T002 → T003 → T004 → T005

# Phase 3 — template tasks sequential; test task parallel:
[P] T010  tests/integration/test_nav_dropdown.py
T006 → T007 → T008 → T009  src/templates/base.html

# Phase 4 — parallel (different files):
[P] T011  src/templates/base.html  (add register link)
[P] T012  tests/integration/test_nav_dropdown.py  (extend assertions)

# Phase 5 — parallel:
[P] T013  pytest full suite
[P] T014  manual quickstart acceptance tests
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup verification
2. Complete Phase 2: Foundational CSS
3. Complete Phase 3: User Story 1 (trigger visible on every page)
4. **STOP and VALIDATE**: `pytest tests/ -v` + manual AC-1 from quickstart.md
5. Continue to Phase 4 (US2) once US1 is confirmed

### Full Delivery (Both Stories)

1. Phases 1–3 (US1)
2. Phase 4 (US2 — register link)
3. Phase 5 (full regression + manual AC tests)
