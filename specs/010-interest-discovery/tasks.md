# Tasks: Interest-Based Discover

**Input**: Design documents from /specs/010-interest-discovery/
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api-contract.md, quickstart.md

**Tests**: Test creation tasks are not included because TDD was not explicitly requested in the specification. Validation execution tasks are included in the final phase.

**Organization**: Tasks are grouped by user story so each story is independently implementable and independently verifiable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Align configuration and baseline constants for interest-driven Discover behavior.

- [X] T001 Define feature-level Discover constants (minimum effective interests and minimum default result count) in src/app.py
- [X] T002 [P] Add helper type hints/documented response keys for personalized listing context in src/services/discovery_service.py
- [X] T003 [P] Add UI placeholder blocks for personalized context and sparse-result messaging in src/templates/home.html

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core building blocks required before user-story implementation.

**CRITICAL**: No user-story work should start until this phase is complete.

- [X] T004 Implement effective-interest context loader (active keys + reconciliation timestamp) in src/services/db.py
- [X] T005 [P] Implement reusable relevance scoring helper for interest/category matching in src/services/discovery_service.py
- [X] T006 [P] Verify and normalize category metadata extraction needed for ranking in src/clients/arxiv_client.py
- [X] T007 Add shared app-level adapter for default Discover context assembly (keys, labels, flags) in src/app.py

**Checkpoint**: Foundation ready - story implementation can begin.

---

## Phase 3: User Story 1 - Personalized Discover Landing (Priority: P1) MVP

**Goal**: Authenticated onboarded users receive default Discover results personalized by their own interests with OR eligibility and relevance-then-recency ordering.

**Independent Test**: Sign in with a user with saved interests, open Discover without manual query, and verify results are personalized from that user context and ordered correctly.

### Implementation for User Story 1

- [X] T008 [US1] Apply personalized default-query behavior for GET / in src/app.py
- [X] T009 [P] [US1] Implement OR-eligible candidate filtering and relevance-then-recency ordering pipeline in src/services/discovery_service.py
- [X] T010 [US1] Apply identical personalized default behavior for GET /api/listings in src/app.py
- [X] T011 [US1] Enforce current-user-only personalization context for web and API listing flows in src/app.py
- [X] T012 [US1] Ensure saved interest updates are reflected on the next Discover load in src/app.py

**Checkpoint**: User Story 1 is fully functional and independently verifiable.

---

## Phase 4: User Story 2 - Transparent Interest Context (Priority: P2)

**Goal**: Users can clearly see which interests are influencing Discover defaults and when defaults are or are not in effect.

**Independent Test**: Open Discover as an onboarded user and confirm active interests are shown; open Discover with manual query and confirm default-interest context is not shown as active.

### Implementation for User Story 2

- [X] T013 [US2] Build active-interest visibility context (keys/labels/default mode flags) for Discover rendering in src/app.py
- [X] T014 [US2] Render active-interest chips/list and default-mode indicator in src/templates/home.html
- [X] T015 [US2] Render onboarding-required guidance path messaging for authenticated users without completed setup in src/templates/home.html
- [X] T016 [US2] Ensure manual query override suppresses default-interest visibility state in src/app.py

**Checkpoint**: User Story 2 is fully functional and independently verifiable.

---

## Phase 5: User Story 3 - Stable Discovery Under Sparse Matches (Priority: P3)

**Goal**: Discover remains usable when direct interest matches are sparse by backfilling with broader recent papers to a fixed minimum count.

**Independent Test**: Use niche interests that yield few direct matches and verify direct matches appear first, broader recent backfill fills to minimum count, and fallback state messaging is clear.

### Implementation for User Story 3

- [X] T017 [US3] Implement direct-vs-backfill classification and merge strategy in src/services/discovery_service.py
- [X] T018 [US3] Enforce fixed minimum default result count using broader recent backfill in src/services/discovery_service.py
- [X] T019 [US3] Propagate backfill_applied and sparse-state flags through listing responses in src/app.py
- [X] T020 [US3] Render sparse/backfill guidance and explicit empty-state guidance in src/templates/home.html
- [X] T021 [US3] Add deterministic tie-break behavior for stable ordering across repeated refreshes in src/services/discovery_service.py

**Checkpoint**: User Story 3 is fully functional and independently verifiable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency checks, docs alignment, and integrated validation.

- [X] T022 [P] Update implementation notes and final validation evidence in specs/010-interest-discovery/quickstart.md
- [X] T023 Run targeted regression validation for Discover and preference behavior via pytest tests/integration/test_discovery_flow.py tests/unit/test_interest_preferences.py
- [X] T024 Run full regression suite and record outcome in specs/010-interest-discovery/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies.
- Foundational (Phase 2): Depends on Setup completion; blocks all user stories.
- User Stories (Phases 3-5): Depend on Foundational completion.
- Polish (Phase 6): Depends on desired user stories being complete.

### User Story Dependencies

- US1 (P1): Starts immediately after Phase 2 and delivers MVP value.
- US2 (P2): Starts after Phase 2; functionally independent but builds on Discover context surfaced by US1 outputs.
- US3 (P3): Starts after Phase 2; functionally independent but integrates best with US1 ordering pipeline.

### Recommended Story Completion Order

- US1 -> US2 -> US3

---

## Parallel Execution Opportunities

- Phase 1: T002 and T003 can run in parallel.
- Phase 2: T005 and T006 can run in parallel after T004 starts context model assumptions.
- US1: T009 can run in parallel with T008 once foundational phase is complete.
- Polish: T022 can run in parallel with T023.

## Parallel Example: User Story 1

- Task T008 in src/app.py
- Task T009 in src/services/discovery_service.py

## Parallel Example: User Story 2

- Task T013 in src/app.py
- Task T014 in src/templates/home.html

## Parallel Example: User Story 3

- Task T017 in src/services/discovery_service.py
- Task T019 in src/app.py

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independent test criteria.
4. Demo/deploy MVP.

### Incremental Delivery

1. Deliver US1 (MVP), validate, and stabilize.
2. Deliver US2 for transparency and user trust.
3. Deliver US3 for sparse-match resilience.
4. Finish with Phase 6 polish and regression evidence.

### Team Parallelization

1. Team aligns on Phase 1 and Phase 2.
2. Developer A: US1 backend orchestration.
3. Developer B: US2 template and context visibility.
4. Developer C: US3 ranking/backfill hardening.
