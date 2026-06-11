# Tasks: Advanced Paper Features

**Input**: Design documents from /specs/012-advanced-paper-features/
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api-contract.md, quickstart.md
**Tests**: **STRICT TDD - FAILING TESTS FIRST!** Every implementation task must have corresponding test task marked "FAILING FIRST" that is completed *before* implementation.
**Organization**: Tasks grouped by user story with clear TDD workflow (TEST FIRST → CODE → REFACTOR)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize dependencies and core structure for advanced features.

- [ ] T001 Update requirements.txt with scikit-learn, pandas, APScheduler
- [ ] T002 [P] Create src/models/advanced_features.py with data class definitions (PaperScore, PaperRelation, PaperNotification, PaperSnapshot, CategoryStats, UserMetadata)
- [ ] T003 [P] Add CSS styles for star ratings, duplicate badges, and notifications in src/static/styles.css
- [ ] T004 [P] Create placeholder for analytics.html template
- [ ] T005 [P] Create src/services/scheduler_service.py with basic APScheduler scaffolding

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database extensions and service framework required before any user story implementation.
**CRITICAL**: No user-story work should start until this phase is complete.

- [ ] T006 Extend src/services/db.py with DB initialization for new tables
- [ ] T007 [P] Implement CRUD operations for PaperSnapshot in src/services/db.py
- [ ] T008 [P] Implement CRUD operations for UserMetadata in src/services/db.py
- [ ] T009 [P] Create src/services/advanced_service.py with basic scaffolding
- [ ] T010 [P] Add paper snapshot persistence to existing paper fetch flow in src/app.py

**Checkpoint**: Foundation ready - story implementation can begin.

---

## Phase 3: User Story 1 - Worth Reading Score (Priority: P1) 🎯 MVP

**Goal**: Every paper displays a 1-5 star "Worth Reading" score based on recency, user relevance, and category popularity.
**Independent Test**: View any paper detail page and verify 1-5 star score appears within 1 second; verify score calculation uses correct weights.

### Tests FIRST (TDD - these must FAIL initially!)

- [ ] T011 [P] [US1] [FAILING FIRST] Write unit test for recency score calculation in tests/unit/test_advanced_features.py
- [ ] T012 [P] [US1] [FAILING FIRST] Write unit test for relevance score calculation in tests/unit/test_advanced_features.py
- [ ] T013 [P] [US1] [FAILING FIRST] Write unit test for category popularity score calculation in tests/unit/test_advanced_features.py
- [ ] T014 [US1] [FAILING FIRST] Write unit test for weighted average score calculator in tests/unit/test_advanced_features.py
- [ ] T015 [US1] [FAILING FIRST] Write integration test for score display on paper detail page in tests/integration/test_advanced_features_flow.py

### Implementation

- [ ] T016 [P] [US1] Implement recency score calculation in src/services/advanced_service.py
- [ ] T017 [P] [US1] Implement relevance score calculation based on user interests in src/services/advanced_service.py
- [ ] T018 [P] [US1] Implement category popularity score calculation in src/services/advanced_service.py
- [ ] T019 [US1] Implement weighted average score calculator in src/services/advanced_service.py
- [ ] T020 [US1] Extend PaperArticle model in src/models/article.py with score display helpers
- [ ] T021 [US1] Integrate score calculation into GET /detail/<paper_id> route in src/app.py
- [ ] T022 [US1] Modify src/templates/detail.html to display 1-5 star "Worth Reading" score

**Checkpoint**: User Story 1 is fully functional and independently verifiable.

---

## Phase 4: User Story 2 - Related Papers (Priority: P2)

**Goal**: Paper detail page shows sidebar with related papers based on title + summary text similarity.
**Independent Test**: Open any paper detail page and verify sidebar shows "Related Papers" section with at least 3 similar papers if available; click a related paper and verify navigation works.

### Tests FIRST (TDD - these must FAIL initially!)

- [ ] T023 [P] [US2] [FAILING FIRST] Write unit test for TF-IDF vectorizer setup in tests/unit/test_advanced_features.py
- [ ] T024 [P] [US2] [FAILING FIRST] Write unit test for cosine similarity calculation in tests/unit/test_advanced_features.py
- [ ] T025 [US2] [FAILING FIRST] Write integration test for related papers display on detail page in tests/integration/test_advanced_features_flow.py

### Implementation

- [ ] T026 [P] [US2] Implement TF-IDF + cosine similarity calculator using scikit-learn in src/services/advanced_service.py
- [ ] T027 [P] [US2] Implement related papers lookup and caching in src/services/advanced_service.py
- [ ] T028 [US2] Add related papers retrieval to GET /detail/<paper_id> route in src/app.py
- [ ] T029 [US2] Extend src/templates/detail.html with sidebar layout for related papers
- [ ] T030 [US2] Implement PaperRelation persistence in src/services/db.py

**Checkpoint**: User Story 2 is fully functional and independently verifiable.

---

## Phase 5: User Story 3 - Duplicate Detection (Priority: P2)

**Goal**: Paper listings show "Duplicate" badge for papers with same arXiv ID.
**Independent Test**: Search/browse and verify duplicate papers (same arXiv ID) show badge; hover shows tooltip.

### Tests FIRST (TDD - these must FAIL initially!)

- [ ] T031 [P] [US3] [FAILING FIRST] Write unit test for normalized arXiv ID comparison in tests/unit/test_advanced_features.py
- [ ] T032 [US3] [FAILING FIRST] Write integration test for duplicate badge display in listings in tests/integration/test_advanced_features_flow.py

### Implementation

- [ ] T033 [P] [US3] Implement duplicate detection helper in src/services/advanced_service.py
- [ ] T034 [P] [US3] Add duplicate badge UI component with tooltip in src/static/styles.css
- [ ] T035 [US3] Integrate duplicate detection into GET / and GET /discover listing routes in src/app.py
- [ ] T036 [US3] Modify src/templates/home.html to show duplicate badges in listings
- [ ] T037 [US3] Modify src/templates/discover.html to show duplicate badges in listings

**Checkpoint**: User Story 3 is fully functional and independently verifiable.

---

## Phase 6: User Story 4 - Trend Analytics Page (Priority: P3)

**Goal**: Dedicated /analytics page shows paper count trends, top authors, and hot keywords using pandas.
**Independent Test**: Navigate to /analytics as signed-in user and verify all trend statistics display; page loads within 5 seconds.

### Tests FIRST (TDD - these must FAIL initially!)

- [ ] T038 [P] [US4] [FAILING FIRST] Write unit test for paper count trend calculation (pandas-based) in tests/unit/test_advanced_features.py
- [ ] T039 [P] [US4] [FAILING FIRST] Write unit test for top authors per category calculation (pandas-based) in tests/unit/test_advanced_features.py
- [ ] T040 [P] [US4] [FAILING FIRST] Write unit test for hot keywords extraction (pandas-based) in tests/unit/test_advanced_features.py
- [ ] T041 [US4] [FAILING FIRST] Write integration test for analytics page display in tests/integration/test_advanced_features_flow.py

### Implementation

- [ ] T042 [P] [US4] Implement paper count trend calculation using pandas in src/services/advanced_service.py
- [ ] T043 [P] [US4] Implement top authors per category calculation using pandas in src/services/advanced_service.py
- [ ] T044 [P] [US4] Implement hot keywords extraction using pandas in src/services/advanced_service.py
- [ ] T045 [US4] Add new GET /analytics route to src/app.py (authenticated only)
- [ ] T046 [US4] Create full src/templates/analytics.html with trend visualizations
- [ ] T047 [US4] Implement CategoryStats persistence in src/services/db.py

**Checkpoint**: User Story 4 is fully functional and independently verifiable.

---

## Phase 7: User Story 5 - New Paper Notifications with APScheduler (Priority: P3)

**Goal**: Background job via APScheduler periodically checks for new relevant papers; users see notifications when logging in.
**Independent Test**: Trigger background job manually, verify new notifications are created; sign out, sign back in, verify notifications display; click navigates to paper, dismiss removes it.

### Tests FIRST (TDD - these must FAIL initially!)

- [ ] T048 [P] [US5] [FAILING FIRST] Write unit test for last_login_at tracking in tests/unit/test_advanced_features.py
- [ ] T049 [P] [US5] [FAILING FIRST] Write unit test for new paper detection logic in tests/unit/test_advanced_features.py
- [ ] T050 [P] [US5] [FAILING FIRST] Write unit test for PaperNotification CRUD operations in tests/unit/test_advanced_features.py
- [ ] T051 [US5] [FAILING FIRST] Write integration test for notification display on login in tests/integration/test_advanced_features_flow.py

### Implementation

- [ ] T052 [P] [US5] Implement last_login_at tracking in src/services/db.py (UserMetadata table)
- [ ] T053 [P] [US5] Implement new paper detection logic in src/services/advanced_service.py
- [ ] T054 [P] [US5] Implement PaperNotification CRUD in src/services/db.py
- [ ] T055 [P] [US5] Implement periodic new paper check background job in src/services/scheduler_service.py using APScheduler
- [ ] T056 [US5] Add APScheduler initialization to app.py startup
- [ ] T057 [US5] Modify src/templates/base.html to add notification display component
- [ ] T058 [US5] Add POST /notification/dismiss and POST /notification/read routes to src/app.py
- [ ] T059 [US5] Implement notification click-through to paper detail

**Checkpoint**: User Story 5 is fully functional and independently verifiable.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Integration, validation, and final quality checks.

- [ ] T060 [P] Update specs/012-advanced-paper-features/quickstart.md with validation notes and outcomes
- [ ] T061 Run targeted feature validation via quickstart.md scenarios
- [ ] T062 Run full regression suite and verify no existing functionality broken
- [ ] T063 Clean up any temporary code and ensure all code follows existing patterns
- [ ] T064 [P] Verify all tests pass (unit + integration)

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies.
- Foundational (Phase 2): Depends on Setup completion; blocks all user stories.
- User Stories (Phases 3-7): Depend on Foundational completion; **each user story MUST follow TDD (tests before code)**
- Polish (Phase 8): Depends on desired user stories being complete.

### User Story Dependencies

- US1 (P1): Starts immediately after Phase 2 - delivers MVP value.
- US2 (P2): Starts after Phase 2 - independent but uses paper data from US1 infrastructure.
- US3 (P2): Starts after Phase 2 - independent but uses listing infrastructure.
- US4 (P3): Starts after Phase 2 - independent but needs PaperSnapshot data.
- US5 (P3): Starts after Phase 2 - independent but needs UserMetadata and PaperSnapshot + scheduler service.

### Recommended Story Completion Order

- US1 → US2 → US3 → US4 → US5

### Critical TDD Reminder

**FOR EVERY TASK IN PHASES 3-7:**
1. ALWAYS write the FAILING TEST FIRST
2. Run the test to CONFIRM it FAILS
3. THEN implement the minimal code to make it PASS
4. THEN refactor if needed

---

## Parallel Execution Opportunities

- Phase 1: T002, T003, T004, T005 can run in parallel.
- Phase 2: T007, T008, T009 can run in parallel after T006.
- US1: T011, T012, T013 can run in parallel (test-writing); then T016, T017, T018 can run in parallel.
- US2: T023, T024 can run in parallel (test-writing); then T026, T027 can run in parallel.
- US3: T031 can be written first, then T033.
- US4: T038, T039, T040 can run in parallel (test-writing); then T042, T043, T044 can run in parallel.
- US5: T048, T049, T050 can run in parallel (test-writing); then T052, T053, T054, T055 can run in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1): **WRITE FAILING TESTS FIRST → THEN CODE**
3. Validate US1 independent test criteria.
4. Demo/deploy MVP.

### Incremental Delivery

1. Deliver US1 (MVP: "Worth Reading" scores) with TDD, validate, stabilize.
2. Deliver US2 (Related Papers) with TDD, validate, stabilize.
3. Deliver US3 (Duplicate Detection) with TDD, validate, stabilize.
4. Deliver US4 (Analytics Page with pandas) with TDD, validate, stabilize.
5. Deliver US5 (Notifications with APScheduler) with TDD, validate, stabilize.
6. Finish with Phase 8 polish and regression evidence.

### Team Parallelization

1. Team aligns on Phase 1 and Phase 2.
2. Developer A: US1 (scoring - TDD)
3. Developer B: US2 (related papers - TDD)
4. Developer C: US3 (duplicate detection - TDD)
5. Developer D: US4 (analytics with pandas - TDD)
6. Developer E: US5 (notifications with APScheduler - TDD)
