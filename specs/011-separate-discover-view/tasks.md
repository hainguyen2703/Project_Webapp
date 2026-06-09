# Tasks: Separate Discover View

**Input**: Design documents from /specs/011-separate-discover-view/
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/api-contract.md, quickstart.md

**Tests**: Dedicated test-first tasks are not included because TDD was not explicitly requested. Validation and regression execution tasks are included in the final phase.

**Organization**: Tasks are grouped by user story so each story remains independently implementable and verifiable.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare route/view scaffolding and shared constants for split Home/Discover behavior.

- [X] T001 Define route and session-state keys for Home/Discover split in src/app.py
- [X] T002 [P] Add navigation placeholders for Home/Discover location cues in src/templates/base.html
- [X] T003 [P] Add discover template scaffold (or shared include placeholder) in src/templates/discover.html

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build reusable route-orchestration helpers required by all stories.

**CRITICAL**: No user-story work starts before this phase is complete.

- [X] T004 Create shared discovery render-context builder for Home/Discover in src/app.py
- [X] T005 [P] Create session-scoped query/filter sync helpers for Home/Discover state in src/app.py
- [X] T006 [P] Add route-access guard helper for authenticated /discover entry in src/app.py
- [X] T007 Add reusable active-route context injector for templates in src/app.py

**Checkpoint**: Foundational helpers complete; user story delivery can begin.

---

## Phase 3: User Story 1 - Access Discover Separately From Home (Priority: P1) MVP

**Goal**: Provide dedicated /discover route while preserving distinct Home route at /.

**Independent Test**: Open / and /discover in same authenticated session and verify each route resolves correctly with dedicated page identity and deep-link support.

### Implementation for User Story 1

- [X] T008 [US1] Implement GET /discover route with dedicated page identity in src/app.py
- [X] T009 [US1] Keep Home route at / and preserve distinct Home view identity in src/app.py
- [X] T010 [P] [US1] Wire Discover route rendering using shared discovery context in src/templates/discover.html
- [X] T011 [US1] Ensure direct /discover bookmark/deep-link entry works for authenticated users in src/app.py
- [X] T012 [US1] Add/adjust integration coverage for route split behavior in tests/integration/test_discovery_flow.py

**Checkpoint**: US1 route split is independently functional and verifiable.

---

## Phase 4: User Story 2 - Keep Discover Behavior Intact in New View (Priority: P2)

**Goal**: Keep search/results behavior functionally identical between / and /discover.

**Independent Test**: Execute equivalent discovery actions on both routes and verify parity for default behavior, manual override, and sparse/empty guidance.

### Implementation for User Story 2

- [X] T013 [US2] Reuse identical discovery search/result orchestration for / and /discover in src/app.py
- [X] T014 [US2] Implement session-only Home/Discover query/filter synchronization (no URL dependency) in src/app.py
- [X] T015 [US2] Ensure sparse/empty guidance rendering parity across both routes in src/templates/home.html
- [X] T016 [P] [US2] Mirror parity guidance blocks in Discover view template in src/templates/discover.html
- [X] T017 [US2] Extend integration coverage for behavior parity and session-only sync in tests/integration/test_discovery_flow.py

**Checkpoint**: US2 behavior parity is independently functional and verifiable.

---

## Phase 5: User Story 3 - Understand Navigation and Current Location (Priority: P3)

**Goal**: Provide clear location cues and predictable navigation/access flow between Home and Discover.

**Independent Test**: Navigate repeatedly between routes and verify active-route cues, /discover auth redirect behavior, and post-login landing on /.

### Implementation for User Story 3

- [X] T018 [US3] Add active-route navigation indicators for Home and Discover in src/templates/base.html
- [X] T019 [US3] Enforce unauthenticated access redirect for /discover in src/app.py
- [X] T020 [US3] Ensure successful login lands on / while preserving explicit navigation to /discover in src/app.py
- [X] T021 [US3] Update login/discovery integration coverage for redirect and landing rules in tests/integration/test_login_flow.py
- [X] T022 [US3] Add integration checks for active-location cue consistency in tests/integration/test_discovery_flow.py

**Checkpoint**: US3 navigation clarity and access behavior are independently functional and verifiable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, documentation alignment, and regression proof.

- [X] T023 [P] Update quickstart validation notes with executed evidence in specs/011-separate-discover-view/quickstart.md
- [X] T024 Run targeted regression tests for login and discovery flows via tests/integration/test_login_flow.py and tests/integration/test_discovery_flow.py
- [X] T025 Run full project regression suite and record outcome in specs/011-separate-discover-view/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): no dependencies.
- Foundational (Phase 2): depends on Phase 1 and blocks all user stories.
- User Stories (Phases 3-5): depend on Phase 2 completion.
- Polish (Phase 6): depends on selected story completion.

### User Story Dependencies

- US1 (P1): starts first after foundational phase and defines route split MVP.
- US2 (P2): depends on US1 route availability for parity verification.
- US3 (P3): can start after US1, then integrates with US2 final navigation cues.

### Suggested Completion Order

- US1 -> US2 -> US3

---

## Parallel Opportunities

- Setup: T002 and T003 can run in parallel.
- Foundational: T005 and T006 can run in parallel.
- US1: T010 can run in parallel with T008 after foundational helpers are ready.
- US2: T016 can run in parallel with T014 once parity context is defined.
- Polish: T023 can run in parallel with T024.

## Parallel Example: User Story 1

- Task T008 in src/app.py
- Task T010 in src/templates/discover.html

## Parallel Example: User Story 2

- Task T014 in src/app.py
- Task T016 in src/templates/discover.html

## Parallel Example: User Story 3

- Task T018 in src/templates/base.html
- Task T021 in tests/integration/test_login_flow.py

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate route split independently.
4. Demo/deploy MVP increment.

### Incremental Delivery

1. Deliver US1 (route split).
2. Deliver US2 (behavior parity + session sync).
3. Deliver US3 (navigation/access clarity).
4. Finish with Phase 6 regression and evidence.

### Team Parallel Plan

1. Team aligns on Setup + Foundational.
2. Developer A: app route/orchestration tasks.
3. Developer B: template/navigation tasks.
4. Developer C: integration test updates.
