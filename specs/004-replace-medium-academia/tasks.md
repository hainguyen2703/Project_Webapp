# Tasks: Replace Medium Source with Academia.edu

**Input**: Design documents from `specs/004-replace-medium-academia/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, quickstart.md ✓  
**Branch**: `004-replace-medium-academia`

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[US1]** / **[US2]**: Which user story this task belongs to
- Exact file paths included in every task description

---

## Phase 1: Setup

**Purpose**: Verify baseline is green before any source files are touched.

- [X] T001 Verify existing test suite passes with `pytest tests/ -v` (expected: 49 tests passing)

**Checkpoint**: All 49 existing tests green — safe to begin.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create the new Academia.edu client module before wiring it into the service and app layers. The service layer change (T005) cannot be written until the client function exists.

- [X] T002 Create `src/clients/academia_client.py` with `fetch_academia_articles(limit, query)` function: `requests.get` with `User-Agent: PaperDiscovery/1.0`, BeautifulSoup4 parse of `div[data-document-id]` containers, per-field selector cascade (title: `a.document-title` → `h3 > a`; author: `span.author-name` → `"Unknown"`; snippet: `p.preview` → `div.document-summary` text → `"No summary available."`; date: `time[datetime]` attr → `span.document-date` text → current UTC ISO; url: `a.document-title[href]` prefixed to `https://www.academia.edu` → `https://www.academia.edu/<doc_id>/`), maps to `PaperArticle` with `source="academia"`, `source_label="Academia.edu"`, default query `"computer science"`
- [X] T003 Add `ACADEMIA_SAMPLE_HTML` inline fixture string and `test_fetch_academia_articles` unit test (with `@patch("src.clients.academia_client.requests.get")`) to `tests/unit/test_source_clients.py`; assert `source == "academia"`, title, authors, snippet in summary, published_at, URL contains `academia.edu`

**Checkpoint**: `pytest tests/unit/test_source_clients.py -v` — new academia test passes alongside arXiv test.

---

## Phase 3: User Story 1 — Academia.edu in source selector, Medium removed (Priority: P1) 🎯 MVP

**Goal**: The home page source selector shows "Academia.edu" and not "Medium". Fetching with `source=academia` returns results. `source=medium` returns an error response.

**Independent Test**: `GET /` HTML contains `value="academia"` and does not contain `value="medium"`. `GET /api/listings?source=academia` returns a `2xx` JSON response. `GET /api/listings?source=medium` returns an error JSON response.

### Implementation for User Story 1

- [X] T004 [P] [US1] In `src/services/discovery_service.py`: replace `from src.clients.medium_client import fetch_medium_articles` with `from src.clients.academia_client import fetch_academia_articles`; replace `elif source == "medium": items = fetch_medium_articles(...)` with `elif source == "academia": items = fetch_academia_articles(...)`
- [X] T005 [P] [US1] In `src/app.py`: replace Medium entry in `CONTENT_SOURCES` list (`{"id": "medium", "name": "Medium", ...}`) with `{"id": "academia", "name": "Academia.edu", "description": "Academic papers from Academia.edu."}` ; replace `"medium"` key with `"academia"` key in `LATEST_RESULTS` dict
- [X] T006 [US1] Delete `src/clients/medium_client.py`
- [X] T007 [US1] In `tests/unit/test_source_clients.py`: remove `from src.clients import ... medium_client` import and `MEDIUM_SAMPLE_RSS` constant and `test_fetch_medium_articles` function (replaced by T003 additions)

**Checkpoint**: `pytest tests/ -v` — all tests pass; `GET /` HTML has `academia` source; no `medium` reference in source selector.

---

## Phase 4: User Story 2 — Detail view works for Academia.edu articles (Priority: P2)

**Goal**: The detail page renders correctly for an Academia.edu article — title, authors, summary, and a working source link are shown.

**Independent Test**: `GET /detail/<encoded_id>?source=academia` with a session-cached article returns a 200 HTML response containing the article fields and a link to `academia.edu`.

### Implementation for User Story 2

- [X] T008 [US2] Verify `src/app.py` item_detail route handles `source=academia` correctly — confirm `LATEST_RESULTS["academia"]` lookup is used (follows naturally from T005); no code change expected; document result in task checklist

**Checkpoint**: Detail view returns 200 for academia source; source link contains `academia.edu`.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final regression guard and manual acceptance test validation.

- [X] T009 [P] Run full test suite `pytest tests/ -v` and confirm all tests pass
- [X] T010 [P] Run quickstart acceptance tests AC-1 through AC-7 from `specs/004-replace-medium-academia/quickstart.md` against `flask run --debug`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 checkpoint — `academia_client.py` must exist before service layer change
- **Phase 3 (US1)**: T004 and T005 depend on Phase 2 (client module must exist); T006–T007 can run in parallel with T004–T005 since they are deletions/removals
- **Phase 4 (US2)**: Depends on Phase 3 (academia source must be wired before detail route can be tested)
- **Phase 5 (Polish)**: Depends on Phase 4

### Within Phase 3

- T004 (`discovery_service.py`) and T005 (`app.py`) edit different files → **[P]** parallel
- T006 (delete `medium_client.py`) and T007 (remove imports/tests in test file) → safe once T002–T003 are done
- T007 must follow T003 (T003 adds the new test before T007 removes the old one — both in same file, do sequentially)

### Parallel Opportunities

```text
# Phase 2:
T002  src/clients/academia_client.py         (new file)
T003  tests/unit/test_source_clients.py      (add fixture + test)
→ T002 and T003 can be done together (different concerns, but T003 imports T002; write T002 first)

# Phase 3:
[P] T004  src/services/discovery_service.py  (swap import + branch)
[P] T005  src/app.py                         (swap source list + cache key)
    T006  DELETE src/clients/medium_client.py
    T007  tests/unit/test_source_clients.py  (remove old medium test — after T003 already added new one)

# Phase 5:
[P] T009  pytest full suite
[P] T010  manual quickstart acceptance tests
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: baseline verification
2. Complete Phase 2: create `academia_client.py` + unit test
3. Complete Phase 3 (US1): wire into service + app, delete medium files
4. **STOP and VALIDATE**: `pytest tests/ -v` + manual AC-1, AC-2, AC-6 from quickstart.md
5. Continue to Phase 4 (US2) once US1 is confirmed

### Full Delivery (Both Stories)

1. Phases 1–3 (US1)
2. Phase 4 (US2 detail view verification)
3. Phase 5 (full regression + manual AC tests)
