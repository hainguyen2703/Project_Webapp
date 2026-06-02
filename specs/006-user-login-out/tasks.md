# Tasks: User Login and Logout

**Input**: Design documents from /specs/006-user-login-out/  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: No explicit test-first or TDD request appears in the specification, so dedicated test tasks are omitted.

**Organization**: Tasks are grouped by user story to keep each story independently implementable and verifiable.

## Format: [ID] [P?] [Story] Description

- [P]: Can run in parallel (different files, no blocking dependency)
- [Story]: User story label for story-phase tasks only
- Every task includes an explicit file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare authentication scaffolding and dependency wiring.

- [X] T001 Add Flask-Login dependency to requirements in requirements.txt
- [X] T002 Create Flask-Login user adapter model in src/models/auth_user.py
- [X] T003 [P] Create authentication service module scaffold in src/services/auth_service.py
- [X] T004 [P] Create login template scaffold in src/templates/login.html

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared auth/session foundations that all stories depend on.

- [X] T005 Wire LoginManager initialization and user loader setup in src/app.py
- [X] T006 [P] Add database helper for account lookup by email/id in src/services/db.py
- [X] T007 [P] Implement core credential verification and LoginAttempt tracking utilities in src/services/auth_service.py
- [X] T008 Implement failed-login throttling and cooldown policy in src/services/auth_service.py
- [X] T009 Implement global session invalidation support primitives in src/services/auth_service.py

**Checkpoint**: Foundation complete; user stories can proceed.

---

## Phase 3: User Story 1 - Sign in with existing account (Priority: P1) 🎯 MVP

**Goal**: Allow valid users to authenticate and use authenticated flows.

**Independent Test**: Submit valid credentials on /login and verify authenticated state is established for subsequent account-enabled access.

### Implementation for User Story 1

- [X] T010 [US1] Add GET /login route and initial form context handling in src/app.py
- [X] T011 [US1] Add POST /login success path using Flask-Login login_user in src/app.py
- [X] T012 [P] [US1] Add login form fields and success/feedback placeholders in src/templates/login.html
- [X] T013 [P] [US1] Add signed-in navigation state in src/templates/base.html
- [X] T014 [US1] Add home-page authenticated status messaging hook in src/templates/home.html

**Checkpoint**: User Story 1 is independently functional and demonstrable.

---

## Phase 4: User Story 2 - Handle invalid sign-in attempts clearly (Priority: P2)

**Goal**: Block invalid authentication attempts with secure, clear feedback.

**Independent Test**: Submit missing/incorrect credentials and rapid repeated failures; verify no authenticated session and appropriate validation/throttle feedback.

### Implementation for User Story 2

- [X] T015 [US2] Implement missing-field and invalid-credential error mapping in src/services/auth_service.py
- [X] T016 [US2] Implement login failure response handling and non-sensitive messaging in src/app.py
- [X] T017 [US2] Implement throttle branch in POST /login handler in src/app.py
- [X] T018 [US2] Render validation and throttle messages in src/templates/login.html
- [X] T019 [P] [US2] Add login error and throttle visual styles in src/static/styles.css

**Checkpoint**: User Story 2 is independently functional without requiring User Story 3 completion.

---

## Phase 5: User Story 3 - Sign out safely (Priority: P3)

**Goal**: Provide secure logout behavior, including signed-out blocking and global invalidation semantics.

**Independent Test**: Logout from authenticated state and verify all sessions are invalidated; verify signed-out logout requests return 401/403 behavior without state changes.

### Implementation for User Story 3

- [X] T020 [US3] Add POST /logout route with authenticated-user path in src/app.py
- [X] T021 [US3] Add signed-out logout blocking behavior (401/403) in src/app.py
- [X] T022 [US3] Invoke global session invalidation for user on logout in src/services/auth_service.py
- [X] T023 [P] [US3] Add logout trigger UI state in src/templates/base.html
- [X] T024 [US3] Add session-expiry auto-refresh handling on protected actions in src/app.py

**Checkpoint**: User Story 3 is independently complete and all stories are functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, hardening, and rollout readiness across all stories.

- [X] T025 [P] Refine auth-related constants/messages for maintainability in src/services/auth_service.py
- [X] T026 [P] Harden auth error responses and logging boundaries in src/app.py
- [X] T027 Align quickstart steps with implemented endpoint behavior in specs/006-user-login-out/quickstart.md
- [X] T028 Run quickstart validation and capture outcomes in specs/006-user-login-out/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1: No dependencies.
- Phase 2: Depends on Phase 1; blocks all user stories.
- Phase 3 (US1): Depends on Phase 2.
- Phase 4 (US2): Depends on Phase 2 and extends login flow behavior.
- Phase 5 (US3): Depends on Phase 2 and authenticated session mechanics from US1.
- Phase 6: Depends on completion of desired user stories.

### User Story Dependencies

- US1 (P1): No dependency on other stories after foundational completion.
- US2 (P2): Builds on login route from US1 but remains independently testable.
- US3 (P3): Relies on authenticated-session creation from US1 and session policy utilities from foundational phase.

### Within Each User Story

- Service logic before route integration.
- Route integration before template rendering updates.
- Core behavior before cross-cutting polish.

---

## Parallel Opportunities

- Setup: T003 and T004 can run in parallel.
- Foundational: T006 and T007 can run in parallel after T005 starts.
- US1: T012 and T013 can run in parallel with route wiring.
- US2: T019 can run in parallel with T016-T018.
- US3: T023 can run in parallel with T022.
- Polish: T025 and T026 can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: T012 [US1] Add login form fields and success/feedback placeholders in src/templates/login.html
Task: T013 [US1] Add signed-in navigation state in src/templates/base.html
```

## Parallel Example: User Story 2

```bash
Task: T016 [US2] Implement login failure response handling and non-sensitive messaging in src/app.py
Task: T019 [US2] Add login error and throttle visual styles in src/static/styles.css
```

## Parallel Example: User Story 3

```bash
Task: T022 [US3] Invoke global session invalidation for user on logout in src/services/auth_service.py
Task: T023 [US3] Add logout trigger UI state in src/templates/base.html
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1) and validate login success path.
3. Demo/deploy MVP if needed.

### Incremental Delivery

1. Deliver US1 (authentication success path).
2. Deliver US2 (invalid login and throttling behavior).
3. Deliver US3 (logout safety and global invalidation).
4. Finish with Phase 6 polish and quickstart validation.

### Parallel Team Strategy

1. Team jointly completes Setup and Foundational phases.
2. Parallel story focus after foundation:
   - Developer A: US1 login flow
   - Developer B: US2 validation and throttling UX
   - Developer C: US3 logout/session invalidation
3. Consolidate for polish and documentation validation.
