# Tasks: User-Owned Favourites

**Input**: Design documents from `/specs/008-user-owned-favourites/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Tests**: No explicit TDD or test-first requirement was specified in the feature specification, so dedicated test-writing tasks are omitted in this task list.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`US1`, `US2`, `US3`)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare implementation scaffolding and remove ambiguity before foundational data/auth changes.

- [x] T001 Document implementation entry points and route ownership mapping in specs/008-user-owned-favourites/quickstart.md
- [x] T002 [P] Add favourites persistence constants and SQL statement placeholders in src/services/db.py
- [x] T003 [P] Add favourites route/auth behavior notes in specs/008-user-owned-favourites/contracts/api-contract.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core persistence and ownership primitives required by all user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T004 Create `favourite_items` table with foreign key to `user_accounts` in src/services/db.py
- [x] T005 Add unique index `(user_id, source, external_paper_id)` in src/services/db.py
- [x] T006 Add index `(user_id, created_at DESC)` for owned favourites listing in src/services/db.py
- [x] T007 Implement favourites CRUD helpers (`add`, `remove`, `list`, `exists`) in src/services/db.py
- [x] T008 Update app-level favourites access to use authenticated `current_user` identity in src/app.py
- [x] T009 Remove legacy anonymous favourites/session-id store paths in src/app.py

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Save Favourites to Account (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can save/unsave papers as their own persistent favourites with duplicate prevention.

**Independent Test**: Sign in as one user, save a paper from detail view, sign out/in, and confirm it remains saved for that same user only.

### Implementation for User Story 1

- [x] T010 [P] [US1] Add canonical `(source, external_paper_id)` extraction helper for favourite actions in src/app.py
- [x] T011 [US1] Implement authenticated-only favourite toggle flow backed by DB in src/app.py
- [x] T012 [US1] Enforce per-user duplicate prevention using DB uniqueness handling in src/services/db.py
- [x] T013 [P] [US1] Update favourite toggle form payload on detail page to include source and item identifier in src/templates/detail.html
- [x] T014 [US1] Render authenticated saved/unsaved favourite state from DB-backed ownership check in src/app.py

**Checkpoint**: User Story 1 is functional and independently demonstrable.

---

## Phase 4: User Story 2 - View and Manage Own Favourites (Priority: P2)

**Goal**: Authenticated users can view and remove only their own favourites in most-recent-first order.

**Independent Test**: Sign in, save two papers in sequence, open favourites (newest first), remove one, and verify list/empty-state behavior updates correctly.

### Implementation for User Story 2

- [x] T015 [US2] Implement authenticated favourites page query with `created_at DESC` ordering in src/app.py
- [x] T016 [US2] Implement authenticated favourite remove route with idempotent behavior in src/app.py
- [x] T017 [P] [US2] Update favourites page rendering for ordered owned list and empty state in src/templates/favourites.html
- [x] T018 [P] [US2] Update shared navigation to show favourites link only for authenticated users in src/templates/base.html

**Checkpoint**: User Stories 1 and 2 both work independently for authenticated users.

---

## Phase 5: User Story 3 - Keep User Favourites Isolated (Priority: P3)

**Goal**: Ensure strict cross-user isolation and account-lifecycle cleanup of favourites.

**Independent Test**: Save favourites as User A, switch to User B and verify no visibility/mutation of User A data, then delete User A account and verify immediate favourite cleanup.

### Implementation for User Story 3

- [x] T019 [US3] Return generic not-found for unauthenticated direct access to `/favourites` and favourite mutation routes in src/app.py
- [x] T020 [US3] Ensure all favourites reads/writes are scoped by authenticated `user_id` in src/services/db.py
- [x] T021 [US3] Implement user-deletion favourites cleanup path with immediate cascade behavior in src/services/db.py

**Checkpoint**: All user stories are independently functional with user isolation guarantees.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, performance, and documentation alignment across all stories.

- [x] T022 [P] Remove obsolete comments and dead favourites code paths after DB migration in src/app.py
- [x] T023 [P] Verify contract/spec/quickstart consistency for auth and favourites ownership language in specs/008-user-owned-favourites/contracts/api-contract.md
- [x] T024 Run quickstart validation scenarios and capture implementation notes in specs/008-user-owned-favourites/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1 and blocks all user stories.
- **User Stories (Phases 3-5)**: Depend on Phase 2 completion.
- **Polish (Phase 6)**: Depends on completion of all targeted user stories.

### User Story Dependencies

- **US1 (P1)**: Starts immediately after Foundational completion; no dependency on other user stories.
- **US2 (P2)**: Starts after Foundational; depends functionally on DB-backed ownership primitives created for US1.
- **US3 (P3)**: Starts after Foundational; validates and hardens isolation/lifecycle constraints across US1 and US2 behavior.

### Within Each User Story

- Route/service identity logic before template wiring for the same operation.
- Data correctness (ownership/uniqueness/order) before UX polish.
- Complete each story checkpoint before moving to next priority when doing incremental delivery.

### Parallel Opportunities

- **Phase 1**: T002 and T003 can run in parallel.
- **Phase 2**: T005 and T006 can run in parallel after T004.
- **US1**: T010 and T013 can run in parallel before final route/state wiring.
- **US2**: T017 and T018 can run in parallel after route behaviors are in place.
- **Polish**: T022 and T023 can run in parallel.

---

## Parallel Example: User Story 1

```bash
# Parallelize canonical key and template payload updates
Task: "T010 [US1] Add canonical (source, external_paper_id) extraction helper in src/app.py"
Task: "T013 [US1] Update favourite toggle form payload in src/templates/detail.html"
```

## Parallel Example: User Story 2

```bash
# Parallelize favourites page and nav presentation updates
Task: "T017 [US2] Update ordered owned list/empty-state rendering in src/templates/favourites.html"
Task: "T018 [US2] Hide favourites navigation for unauthenticated users in src/templates/base.html"
```

## Parallel Example: User Story 3

```bash
# Parallelize isolation hardening workstreams
Task: "T019 [US3] Enforce generic not-found on unauthenticated favourites route access in src/app.py"
Task: "T020 [US3] Scope all favourites DB operations to authenticated user_id in src/services/db.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup).
2. Complete Phase 2 (Foundational).
3. Complete Phase 3 (US1).
4. Validate US1 independent test end-to-end.
5. Demo/deploy MVP behavior.

### Incremental Delivery

1. Build foundation once (Phases 1-2).
2. Deliver US1 (save/unsave persistence).
3. Deliver US2 (owned list + remove + ordering).
4. Deliver US3 (strict isolation + unauth not-found + lifecycle cleanup).
5. Finish with Phase 6 consistency and quickstart validation.

### Parallel Team Strategy

1. Team aligns on Phase 2 schema and DB helpers together.
2. After Phase 2:
   - Developer A: US1 route and detail toggle state
   - Developer B: US2 favourites page and navigation updates
   - Developer C: US3 isolation hardening and account cleanup behavior
3. Rejoin for Phase 6 cross-cutting validation.

---

## Notes

- [P] tasks are scoped to different files and can be executed concurrently.
- User story labels preserve traceability from tasks to spec priorities.
- Each phase has a clear checkpoint for independent validation.
- Keep commits scoped by task or tightly related task group.
