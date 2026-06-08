# Tasks: User Interest Selection Onboarding

**Input**: Design documents from `/specs/009-build-user-interest-onboarding/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: The specification does not explicitly request TDD-first or dedicated test-authoring tasks. This task list focuses on implementation tasks plus end-to-end validation execution.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`US1`, `US2`, `US3`)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare feature scaffolding and align docs/contracts before core implementation.

- [X] T001 Add onboarding/interest flow implementation mapping notes in specs/009-build-user-interest-onboarding/quickstart.md
- [X] T002 [P] Create route/behavior stub notes for onboarding endpoints in specs/009-build-user-interest-onboarding/contracts/api-contract.md
- [X] T003 [P] Add feature-level TODO markers for new onboarding templates in src/templates/onboarding_interests.html
- [X] T004 [P] Add feature-level TODO markers for interest management template in src/templates/interests.html

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Data model and persistence groundwork required by all user stories.

**CRITICAL**: No user story work starts before this phase completes.

- [X] T005 Add `interest_topics` catalog table schema in src/services/db.py
- [X] T006 Add `user_interest_preferences` metadata table schema in src/services/db.py
- [X] T007 Add `user_interest_selections` table schema with ownership foreign keys in src/services/db.py
- [X] T008 Add uniqueness/index constraints for `(user_id, interest_key)` and catalog lookups in src/services/db.py
- [X] T009 Implement DB helpers to read active catalog/default topics in src/services/db.py
- [X] T010 Implement DB helpers to save/list/update user interest selections in src/services/db.py
- [X] T011 Implement retired-interest cleanup and minimum auto-fill helpers in src/services/db.py
- [X] T012 Implement onboarding completion state helpers in src/services/db.py

**Checkpoint**: Foundation ready for onboarding and discovery behavior work.

---

## Phase 3: User Story 1 - Select Interests During Onboarding (Priority: P1) MVP

**Goal**: New or first-time authenticated users must complete interest onboarding before entering discovery.

**Independent Test**: Sign in as a user with no preferences, confirm redirect to onboarding, submit valid interests, and confirm discovery access is unlocked.

### Implementation for User Story 1

- [X] T013 [US1] Add post-auth onboarding gate logic for discovery/home access in src/app.py
- [X] T014 [US1] Implement GET `/onboarding/interests` route behavior in src/app.py
- [X] T015 [US1] Implement POST `/onboarding/interests` validation and persistence flow in src/app.py
- [X] T016 [P] [US1] Build onboarding interest selection page with catalog choices and validation rendering in src/templates/onboarding_interests.html
- [X] T017 [US1] Wire onboarding-completion updates to per-user state helpers in src/services/db.py

**Checkpoint**: US1 can be validated independently and delivers onboarding gate + completion flow.

---

## Phase 4: User Story 2 - Manage Interests After Onboarding (Priority: P2)

**Goal**: Onboarded users can view and update account-owned interest selections.

**Independent Test**: Open interest management as onboarded user, verify pre-populated selections, submit updates, and confirm persistence across sign-out/sign-in.

### Implementation for User Story 2

- [X] T018 [US2] Implement GET `/interests` route with authenticated access and pre-populated selections in src/app.py
- [X] T019 [US2] Implement POST `/interests` route with catalog-only and min/max validation in src/app.py
- [X] T020 [P] [US2] Build interest management page UI and validation feedback in src/templates/interests.html
- [X] T021 [US2] Add authenticated navigation link to interest management in src/templates/base.html
- [X] T022 [US2] Ensure preference updates replace prior selection set for current user only in src/services/db.py

**Checkpoint**: US2 independently validates update lifecycle without depending on US3 behavior.

---

## Phase 5: User Story 3 - Apply Interests to Discovery Defaults (Priority: P3)

**Goal**: Discovery defaults are derived from saved interests using OR matching and lifecycle cleanup rules.

**Independent Test**: For an onboarded user, verify discovery defaults reflect any selected interest; retire interests and verify automatic removal plus default auto-fill when below minimum.

### Implementation for User Story 3

- [X] T023 [US3] Inject OR-based interest defaults into discovery route when no manual override is provided in src/app.py
- [X] T024 [US3] Apply interest-derived default context in discovery template rendering in src/templates/home.html
- [X] T025 [US3] Integrate retired-interest cleanup and minimum auto-fill in authenticated request flow in src/app.py
- [X] T026 [US3] Enforce account-deletion cleanup for interest preference metadata and selections in src/services/db.py
- [X] T027 [US3] Ensure discovery default preparation uses active catalog membership only in src/services/db.py

**Checkpoint**: All user stories are independently functional with lifecycle and defaulting rules in place.

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Final consistency pass, docs sync, and end-to-end validation.

- [X] T028 [P] Remove obsolete onboarding/interest TODO placeholders and dead branches in src/app.py
- [X] T029 [P] Reconcile final contract wording with implemented route behavior in specs/009-build-user-interest-onboarding/contracts/api-contract.md
- [X] T030 [P] Capture final validation run notes and outcomes in specs/009-build-user-interest-onboarding/quickstart.md
- [X] T031 Execute full quickstart validation scenarios and document pass/fail results in specs/009-build-user-interest-onboarding/quickstart.md

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, starts immediately.
- **Foundational (Phase 2)**: Depends on Setup; blocks all user stories.
- **User Stories (Phases 3-5)**: Depend on Foundational completion.
- **Polish (Phase 6)**: Depends on completion of selected user stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational, no dependency on US2/US3.
- **US2 (P2)**: Starts after Foundational and reuses persistence from US1.
- **US3 (P3)**: Starts after Foundational and integrates with behaviors from US1/US2.

### Within Each User Story

- Route behavior and validation before UI refinements.
- Persistence correctness before discovery/default integration.
- Story checkpoint must pass before moving to next priority in incremental delivery.

### Parallel Opportunities

- **Setup**: T002, T003, T004 can run in parallel.
- **Foundational**: T009 and T010 can run in parallel after schema/index tasks.
- **US1**: T016 can run in parallel with route implementation T014/T015.
- **US2**: T020 and T021 can run in parallel after route contract is defined.
- **Polish**: T028, T029, and T030 can run in parallel before T031.

---

## Parallel Example: User Story 1

```bash
Task: "T014 [US1] Implement GET /onboarding/interests route behavior in src/app.py"
Task: "T016 [US1] Build onboarding interest selection page in src/templates/onboarding_interests.html"
```

## Parallel Example: User Story 2

```bash
Task: "T019 [US2] Implement POST /interests validation and persistence flow in src/app.py"
Task: "T020 [US2] Build interest management page UI in src/templates/interests.html"
```

## Parallel Example: User Story 3

```bash
Task: "T023 [US3] Inject OR-based defaults into discovery route in src/app.py"
Task: "T027 [US3] Ensure defaults use active catalog membership in src/services/db.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational).
3. Complete Phase 3 (US1).
4. Validate US1 independently before expanding scope.

### Incremental Delivery

1. Setup + Foundational create stable base.
2. Deliver US1 (mandatory onboarding gate + completion).
3. Deliver US2 (interest management updates).
4. Deliver US3 (OR defaults + retired-interest lifecycle behavior).
5. Finish with polish and full quickstart validation.

### Parallel Team Strategy

1. Team completes foundational schema/helpers together.
2. After foundation:
   - Developer A: US1 onboarding routes + screen
   - Developer B: US2 management routes + navigation
   - Developer C: US3 discovery-default and lifecycle integration
3. Merge into Phase 6 polish and final validation.

---

## Notes

- [P] tasks touch separate files/concerns and can be executed concurrently.
- Story labels map tasks to spec priorities for traceability.
- Each user story has an explicit independent test checkpoint.
- Keep commits grouped by task or logical task slice.
