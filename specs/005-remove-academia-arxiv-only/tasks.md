# Tasks: Remove Academia.edu — arXiv Only

**Input**: Design documents from `specs/005-remove-academia-arxiv-only/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓  
**Branch**: `005-remove-academia-arxiv-only`

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[US1]** / **[US2]**: Which user story this task belongs to
- Exact file paths included in every task description

---

## Phase 1: Setup

**Purpose**: Verify baseline is green before any source files are touched.

- [X] T001 Verify existing test suite passes with `python -m pytest tests/ -v` (expected: 49 tests passing)

**Checkpoint**: All 49 existing tests green — safe to begin.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Remove the Academia.edu import chain in dependency order so the codebase is never in a broken-import state. The `discovery_service.py` import must be removed *before* the client file is deleted; otherwise any test run between the two steps would fail with `ModuleNotFoundError`.

- [X] T002 In `src/services/discovery_service.py`: remove the line `from src.clients.academia_client import fetch_academia_articles` and remove the `elif source == "academia": items = fetch_academia_articles(limit=limit, query=query)` branch from `fetch_items()`
- [X] T003 Delete `src/clients/academia_client.py` entirely (depends on T002 — import already removed)

**Checkpoint**: `python -m pytest tests/unit/test_source_clients.py tests/unit/test_models.py -v` — all existing unit tests still pass; no `ModuleNotFoundError`.

---

## Phase 3: User Story 1 — Academia.edu Removed, arXiv Fetch Works (Priority: P1) 🎯 MVP

**Goal**: The home page shows no source selector and no Academia.edu reference. The `/api/listings` endpoint always returns arXiv results. The `source=academia` parameter is silently ignored. All related tests are updated to match the new behaviour.

**Independent Test**: `GET /` rendered HTML contains no `<select>` or `value="academia"`. `GET /api/listings` returns arXiv JSON. `GET /api/listings?source=academia` returns identical arXiv JSON. All 48 automated tests pass.

### Implementation for User Story 1

- [X] T004 [P] [US1] In `src/app.py`: (1) remove the `CONTENT_SOURCES` list entirely; (2) change `LATEST_RESULTS` to `{"arxiv": []}` removing the `"academia"` key; (3) in `home()` replace `selected_source = request.args.get("source", "arxiv")` with `selected_source = "arxiv"` and remove `"sources": CONTENT_SOURCES` from the context dict; (4) replace the full body of `api_listings()` with `source = "arxiv"` / `query = request.args.get("query")` / `result = fetch_items(source, query=query)` / return 503 on error else 200; (5) in `item_detail()` replace `source = request.args.get("source", "arxiv")` with `source = "arxiv"`
- [X] T005 [P] [US1] In `src/templates/home.html`: (1) remove the `<label for="source">Source</label>` element; (2) remove the entire `<select id="source" name="source">…</select>` block; (3) change `<h2>Results from {{ selected_source | capitalize }}</h2>` to `<h2>Results from arXiv</h2>`; (4) change the detail link `url_for('item_detail', item_id=item.id, source=selected_source)` to `url_for('item_detail', item_id=item.id)`; (5) change the retry link `url_for('home', source=selected_source, query=query, fetch=1)` to `url_for('home', query=query, fetch=1)`
- [X] T006 [P] [US1] In `tests/unit/test_source_clients.py`: (1) change the import line from `from src.clients import arxiv_client, academia_client` to `from src.clients import arxiv_client`; (2) remove the `ACADEMIA_SAMPLE_HTML` constant (the multi-line string); (3) remove the entire `test_fetch_academia_articles` function
- [X] T007 [US1] In `tests/integration/test_discovery_flow.py`: (1) in `test_homepage_displays_results` change `client.get("/?source=arxiv&fetch=1")` to `client.get("/?fetch=1")` and change `assert b"Results from Arxiv"` to `assert b"Results from arXiv"`; (2) in `test_detail_view_shows_source_link` change `client.get("/?source=arxiv&fetch=1")` to `client.get("/?fetch=1")` and change `client.get("/detail/http://arxiv.org/abs/1234.5678v1?source=arxiv")` to `client.get("/detail/http://arxiv.org/abs/1234.5678v1")`; (3) in `test_error_state_shows_retry` change `client.get("/?source=medium&fetch=1")` to `client.get("/?fetch=1")`

**Checkpoint**: `python -m pytest tests/ -v` — 48 tests pass; `GET /` HTML has no `<select>`; `GET /api/listings` returns arXiv JSON; `GET /api/listings?source=academia` also returns arXiv JSON.

---

## Phase 4: User Story 2 — arXiv Detail View Remains Functional (Priority: P2)

**Goal**: The detail page renders correctly for an arXiv article after the source cleanup. The "Return to list" link navigates back to the home page without any stale `source=` parameter.

**Independent Test**: Fetch arXiv results, then `GET /detail/<id>` (no source param) returns 200 with article fields and a link to `arxiv.org`. The "Return to list" link URL contains no `source=` parameter.

### Implementation for User Story 2

- [X] T008 [US2] In `src/templates/detail.html`: change `url_for('home', source=source, fetch=1)` to `url_for('home', fetch=1)` in the "Return to list" anchor tag

**Checkpoint**: Detail view returns 200 for arXiv articles; "Return to list" URL contains no `source=` parameter.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final regression guard and manual acceptance test validation.

- [X] T009 [P] Run full test suite `python -m pytest tests/ -v` and confirm exactly 48 tests pass (49 minus the removed `test_fetch_academia_articles`)
- [X] T010 [P] Run quickstart acceptance tests AC-1 through AC-7 from `specs/005-remove-academia-arxiv-only/quickstart.md` against `python -m flask --app src.app run --debug`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 checkpoint — T002 must precede T003 (import removed before file deleted)
- **Phase 3 (US1)**: T004, T005, T006 depend on Phase 2 (academia client must be gone); T007 depends on T004 + T005 (tests must reflect new app behaviour)
- **Phase 4 (US2)**: T008 is independent of Phase 3 at the file level (different file), but logically follows US1 completion
- **Phase 5 (Polish)**: Depends on Phase 4

### Within Phase 2

- **T002 → T003** (strictly sequential): remove the import first, then delete the file to avoid `ModuleNotFoundError`

### Within Phase 3

- **T004** (`src/app.py`), **T005** (`src/templates/home.html`), **T006** (`tests/unit/test_source_clients.py`) → **[P]** all edit different files, no shared state
- **T007** (`tests/integration/test_discovery_flow.py`) → must follow T004 + T005; integration tests exercise the live routes

### Parallel Opportunities

```text
# Phase 2 (sequential only):
T002  src/services/discovery_service.py  (remove import + branch)
T003  src/clients/academia_client.py     (DELETE — after T002)

# Phase 3 (parallel start, sequential finish):
[P] T004  src/app.py                              (routes + config)
[P] T005  src/templates/home.html                 (selector removal)
[P] T006  tests/unit/test_source_clients.py       (remove academia test)
    T007  tests/integration/test_discovery_flow.py (update assertions — after T004+T005)

# Phase 4 (independent):
    T008  src/templates/detail.html                (return link fix)

# Phase 5 (parallel):
[P] T009  pytest full suite
[P] T010  manual quickstart AC tests
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: baseline verification
2. Complete Phase 2: remove academia from service layer
3. Complete Phase 3 (US1): simplify app + templates + tests
4. **STOP and VALIDATE**: `python -m pytest tests/ -v` + manual AC-1, AC-2, AC-5 from quickstart.md
5. Continue to Phase 4 (US2) once US1 is confirmed

### Full Delivery (Both Stories)

1. Phases 1–3 (US1)
2. Phase 4 (US2 detail return link)
3. Phase 5 (full regression + manual AC tests)
