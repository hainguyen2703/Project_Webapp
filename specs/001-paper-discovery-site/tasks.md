# Tasks: Paper Discovery Website

**Input**: Design documents from `specs/001-paper-discovery-site/`
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `contracts/`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the repository structure, dependencies, and the baseline website architecture.

- [ ] T001 Create the Python web application entrypoint in `src/app.py`
- [ ] T002 Create the source client package in `src/clients/`
- [ ] T003 Create the service layer package in `src/services/`
- [ ] T004 Create the template directory in `src/templates/` and static assets directory in `src/static/`
- [ ] T005 [P] Add a baseline stylesheet in `src/static/styles.css`
- [ ] T006 [P] Add an initial HTML template skeleton in `src/templates/base.html`
- [ ] T007 [P] Create `tests/unit/` and `tests/integration/` directories
- [ ] T008 Add `requirements.txt` or `pyproject.toml` references for Python, FastAPI/Flask, Jinja2, HTTPX/Requests, BeautifulSoup/lxml, pytest, Black, and Flake8

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build the core fetch and display model, routing, and error handling that all stories depend on.

- [ ] T009 Define the `PaperArticle` model in `src/models/article.py`
- [ ] T010 Define the `ContentSource` model in `src/models/source.py`
- [ ] T011 Implement the arXiv fetch client in `src/clients/arxiv_client.py`
- [ ] T012 Implement the Medium fetch client in `src/clients/medium_client.py`
- [ ] T013 Implement the discovery service in `src/services/discovery_service.py`
- [ ] T014 [P] Add reusable fetch result handling and status normalization in `src/services/result_formatter.py`
- [ ] T015 Implement the `/api/listings` backend endpoint and contract-compatible source listing response shape in `src/app.py`
- [ ] T016 Implement error handling and retry guidance for source fetch failures in `src/app.py`
- [ ] T017 [P] Add unit tests for source parsing and model validation in `tests/unit/test_models.py`
- [ ] T018 [P] Add unit tests for arXiv and Medium clients in `tests/unit/test_source_clients.py`
- [ ] T019 [P] Add a smoke integration test for the discovery endpoint in `tests/integration/test_discovery_flow.py`

**Checkpoint**: After these tasks, the project should be able to fetch and normalize source results and render them through the web application without story-specific UI polish.

---

## Phase 3: User Story 1 - Discover research and articles (Priority: P1) 🎯 MVP

**Goal**: Enable visitors to choose arXiv or Medium and view a readable list of items.

**Independent Test**: Load the homepage, choose a source, and verify that a list of papers/articles appears with title, author, source label, summary, and date.

### Implementation for User Story 1

- [ ] T020 [US1] Add source selection and list rendering in `src/templates/home.html`
- [ ] T021 [US1] Add a controller/view for the homepage and source selection in `src/app.py`
- [ ] T022 [US1] Render normalized `PaperArticle` cards with title, authors, summary, source label, and publish date in `src/templates/home.html`
- [ ] T023 [US1] Style the discovery list for readability and source distinction in `src/static/styles.css`
- [ ] T024 [US1] Add a list-focused integration test for the discovery flow in `tests/integration/test_discovery_flow.py`
- [ ] T025 [US1] Document the source selection behavior in `specs/001-paper-discovery-site/quickstart.md`

**Checkpoint**: User Story 1 should be fully functional and independently testable by selecting a source and viewing a list.

---

## Phase 4: User Story 2 - Read paper details in a simple UI (Priority: P2)

**Goal**: Let visitors inspect a content item and see details without losing the selected source or list state.

**Independent Test**: Select an item from the list and confirm the detail view presents metadata clearly, then return to the list with the same source context.

### Implementation for User Story 2

- [ ] T026 [US2] Add item detail route in `src/app.py`
- [ ] T027 [US2] Create `src/templates/detail.html` for expanded item metadata
- [ ] T028 [US2] Render a direct source link to the original arXiv or Medium item in `src/templates/detail.html`
- [ ] T029 [US2] Preserve selected source and back navigation state in `src/app.py`
- [ ] T030 [US2] Add detail view styling in `src/static/styles.css`
- [ ] T031 [US2] Add an integration test for the detail view and context preservation in `tests/integration/test_discovery_flow.py`

**Checkpoint**: User Story 2 should be independently functional with a working item detail view and list return path.

---

## Phase 5: User Story 3 - See a friendly response when a source is unavailable (Priority: P3)

**Goal**: Ensure the website shows a clear error state and retry option when arXiv or Medium fetch fails or returns no results.

**Independent Test**: Simulate a source failure or empty result and verify the UI displays a readable recovery message and retry control.

### Implementation for User Story 3

- [ ] T032 [US3] Add user-facing error state handling to `src/templates/home.html`
- [ ] T033 [US3] Implement retry behavior and empty-state messaging in `src/app.py`
- [ ] T034 [US3] Style error and empty-state messaging in `src/static/styles.css`
- [ ] T035 [US3] Add an integration test for source failure and empty-state handling in `tests/integration/test_discovery_flow.py`
- [ ] T036 [US3] Add a contract-style validation test for normalized fetch responses in `tests/unit/test_models.py`

**Checkpoint**: User Story 3 should be independently functional with clear error recovery and empty-state messaging.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Complete quality work, documentation, and release readiness.

- [ ] T037 [P] Add logging and request timing instrumentation in `src/app.py`
- [ ] T038 [P] Run Black and Flake8 across `src/` and `tests/`
- [ ] T039 [P] Update `specs/001-paper-discovery-site/quickstart.md` with exact run instructions and dependencies
- [ ] T040 [P] Add or refine README notes for the feature in `README.md` or project documentation
- [ ] T041 [P] Perform a final browser smoke test for the homepage, list view, detail view, and error flows
- [ ] T042 [P] Conduct a quick usability validation round for the discovery flow and capture findings in `specs/001-paper-discovery-site/quickstart.md`
- [ ] T043 [P] Add a performance timing or caching validation check for source fetch latency in `tests/integration/test_discovery_flow.py` or `src/app.py`
- [ ] T044 [P] Verify user-facing error and retry messaging matches the acceptance criteria in `tests/integration/test_discovery_flow.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user story implementation.
- **User Stories (Phase 3+)**: Depend on Foundational phase completion.
- **Polish (Final Phase)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational; no dependency on other stories.
- **User Story 2 (P2)**: Can start after Foundational; should be independently testable from US1.
- **User Story 3 (P3)**: Can start after Foundational; should be independently testable from US1 and US2.

### Parallel Opportunities

- Setup tasks in Phase 1 can run in parallel where they affect different files.
- Foundational tasks T009-T019 include parallelizable client/model/test work.
- User Story phases can be worked on in parallel by different developers after Foundation completes.
- Polish tasks T037-T044 can run in parallel with final cleanup and validation.
