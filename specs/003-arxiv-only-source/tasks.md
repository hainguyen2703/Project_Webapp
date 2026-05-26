# Tasks: Simplify to arXiv-Only Source

**Input**: Design documents from `/specs/003-arxiv-only-source/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete tasks)
- **[Story]**: User story this task belongs to (US1 = arXiv-only feed, US2 = Home button)

---

## Phase 1: Setup

**Purpose**: Confirm baseline state before any changes are made

- [X] T001 Run `pytest tests/` from project root and confirm all existing tests pass before starting changes

---

## Phase 2: Foundational — Delete Medium Backend

**Purpose**: Remove Medium source from the backend entirely. Both user stories depend on this being complete.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Delete `src/clients/medium_client.py` entirely
- [X] T003 Remove the `from src.clients.medium_client import fetch_medium_articles` import and the `elif source == "medium":` branch (including its body) from `src/services/discovery_service.py`

**Checkpoint**: Backend no longer references Medium. `python -m src.app` must start without import errors.

---

## Phase 3: User Story 1 — arXiv-Only Paper Feed (Priority: P1) 🎯 MVP

**Goal**: Users see only arXiv papers on the home page with no source-selection step.

**Independent Test**: `GET /?fetch=1` returns HTTP 200; rendered HTML contains paper cards attributed to arXiv and contains no `<select>` element for source selection.

- [X] T004 [P] [US1] Simplify `src/app.py`: remove the `CONTENT_SOURCES` list, change `LATEST_RESULTS` to `{"arxiv": []}`, replace `selected_source = request.args.get("source", "arxiv")` with `selected_source = "arxiv"`, and remove `"sources"` and `"selected_source"` keys from the `context` dict passed to `render_template`
- [X] T005 [P] [US1] Remove the source `<label>` and `<select id="source" name="source">` block from `src/templates/home.html`, keeping the query input and Fetch Listings button intact
- [X] T006 [P] [US1] Remove the `from src.clients import medium_client` import, the `MEDIUM_SAMPLE_RSS` fixture string, and the `test_fetch_medium_articles` function from `tests/unit/test_source_clients.py`
- [X] T007 [P] [US1] Update `test_error_state_shows_retry` in `tests/integration/test_discovery_flow.py`: change the mock return value `source` field from `"medium"` to `"arxiv"` and `error_message` to `"arXiv is unavailable."`, and update the route called to `/?source=arxiv&fetch=1`

**Checkpoint**: US1 fully functional — home page shows arXiv-only results; no source dropdown visible; `pytest tests/unit/test_source_clients.py` and `pytest tests/integration/test_discovery_flow.py` pass.

---

## Phase 4: User Story 2 — Home Button Navigation (Priority: P2)

**Goal**: A "Home" button is visible in the header on all pages and returns the user to the home page with a fresh arXiv fetch.

**Independent Test**: `GET /` and `GET /detail/{id}` both return HTML containing the text `Home` in the header; clicking the link navigates to `/?fetch=1`.

- [X] T008 [P] [US2] Add a Home button anchor to the `<header>` block in `src/templates/base.html`: `<a class="home-btn" href="{{ url_for('home', fetch=1) }}">Home</a>` placed after the `<h1>` and `<p>` description
- [X] T009 [P] [US2] Update the "Return to list" `<a>` link in `src/templates/detail.html` to use `href="{{ url_for('home', fetch=1) }}"` (remove the `source=source` argument) and update its visible text to `Home`
- [X] T010 [P] [US2] Add `.home-btn` styles to `src/static/styles.css`: display it as an inline-block link with padding consistent with the existing button style, and a contrasting colour that matches the header
- [X] T011 [US2] Add a `test_home_button_visible` test to `tests/integration/test_discovery_flow.py` (after the existing tests): assert that a `GET /` response and a `GET /detail/{id}` response both contain `b'Home'` in their HTML

**Checkpoint**: US2 fully functional — "Home" button appears in the header on the home page and the detail page; clicking it reloads arXiv results; `pytest tests/integration/test_discovery_flow.py` passes.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation against the full spec and quickstart.

- [X] T012 [P] Run the full test suite — `pytest tests/` from the project root — and confirm zero failures and zero import errors related to Medium
- [X] T013 Validate against `specs/003-arxiv-only-source/quickstart.md`: start the app (`python -m src.app`), open `http://localhost:8000`, fetch arXiv papers, navigate to a detail page, confirm "Home" button is present, click it and confirm papers reload — all acceptance scenarios in the quickstart must pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **blocks all user stories**
- **US1 (Phase 3)**: Depends on Phase 2 completion
- **US2 (Phase 4)**: Depends on Phase 2 completion — can run in parallel with US1 (different files)
- **Polish (Phase 5)**: Depends on all desired user stories complete

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2 — no dependency on US2
- **US2 (P2)**: Starts after Phase 2 — no dependency on US1 *(exception: T011 edits the same file as T007; T011 must run after T007)*

### Within Each User Story

- T004, T005, T006, T007 are all [P] (different files — can be worked simultaneously)
- T008, T009, T010 are all [P] (different files — can be worked simultaneously)
- T011 must come after T007 (both edit `tests/integration/test_discovery_flow.py`)

---

## Parallel Opportunities

### Phase 3 — all US1 tasks in parallel

```
T004  src/app.py
T005  src/templates/home.html
T006  tests/unit/test_source_clients.py
T007  tests/integration/test_discovery_flow.py
```

### Phase 4 — T008/T009/T010 in parallel, then T011

```
T008  src/templates/base.html
T009  src/templates/detail.html
T010  src/static/styles.css

→ then T011  tests/integration/test_discovery_flow.py  (after T007)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational — delete Medium backend (T002, T003)
3. Complete Phase 3: User Story 1 (T004–T007)
4. **STOP and VALIDATE**: `pytest tests/` passes; home page shows arXiv-only feed; no dropdown
5. Proceed to Phase 4 (US2) when ready

### Full Delivery

1. Phase 1 → 2 → 3 (US1) → 4 (US2) → 5 (Polish)
2. US2 can begin in parallel with US1 after Phase 2 (except T011 which follows T007)
