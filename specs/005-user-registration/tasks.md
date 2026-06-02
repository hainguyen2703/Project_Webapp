# Tasks: User Registration

**Input**: Design documents from `/specs/005-user-registration/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: No explicit TDD/test-first requirement was requested in the feature spec, so test tasks are not included.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (`[US1]`, `[US2]`, `[US3]`)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize registration-related structure and entry points.

- [X] T001 Create SQLite data directory placeholder in src/data/.gitkeep
- [X] T002 Create database utility module scaffold in src/services/db.py
- [X] T003 [P] Create registration service module scaffold in src/services/registration_service.py
- [X] T004 [P] Create registration page template scaffold in src/templates/register.html

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core plumbing that blocks all user-story implementation until complete.

- [X] T005 Implement SQLite connection and schema bootstrap for user accounts in src/services/db.py
- [X] T006 [P] Wire database initialization into app startup in src/app.py
- [X] T007 [P] Implement Werkzeug password-hash and account creation helpers in src/services/registration_service.py
- [X] T008 Implement in-flight submission token guard utilities in src/services/registration_service.py
- [X] T009 Add shared registration form/message styles in src/static/styles.css

**Checkpoint**: Foundation complete. User stories can now proceed.

---

## Phase 3: User Story 1 - Create a new account (Priority: P1) 🎯 MVP

**Goal**: Allow visitors to register successfully and become active immediately.

**Independent Test**: Submit valid email/password on `/register` and verify redirect success plus active account persistence.

### Implementation for User Story 1

- [X] T010 [US1] Add `GET /register` route and template context in src/app.py
- [X] T011 [US1] Implement `POST /register` success path (first-flight submit, account create, active status, redirect) in src/app.py
- [X] T012 [P] [US1] Add Register navigation link to shared header in src/templates/base.html
- [X] T013 [P] [US1] Add registration success banner handling on home page in src/templates/home.html
- [X] T014 [US1] Implement registration form fields and submission token handling in src/templates/register.html

**Checkpoint**: User Story 1 is fully functional and independently demonstrable.

---

## Phase 4: User Story 2 - Prevent invalid registrations (Priority: P2)

**Goal**: Reject invalid submissions with clear, actionable user feedback.

**Independent Test**: Submit invalid/missing fields and weak passwords; verify registration is blocked and field-level guidance is shown.

### Implementation for User Story 2

- [X] T015 [US2] Implement required-field validation and password policy rules in src/services/registration_service.py
- [X] T016 [US2] Implement leading/trailing whitespace email rejection in src/services/registration_service.py
- [X] T017 [US2] Map validation failures to structured field errors in `POST /register` handler in src/app.py
- [X] T018 [US2] Render field-level error messages and preserve non-sensitive input in src/templates/register.html
- [X] T019 [P] [US2] Add validation error-state styling in src/static/styles.css

**Checkpoint**: User Story 2 is independently functional and does not require US3 behavior.

---

## Phase 5: User Story 3 - Handle duplicate identity gracefully (Priority: P3)

**Goal**: Prevent duplicate account creation and provide clear duplicate-email feedback.

**Independent Test**: Attempt registration with an existing email and verify no second account is created and user sees guidance.

### Implementation for User Story 3

- [X] T020 [US3] Implement duplicate-email lookup helper in src/services/registration_service.py
- [X] T021 [US3] Add duplicate-email handling branch in `POST /register` handler in src/app.py
- [X] T022 [US3] Render duplicate-email guidance on registration form in src/templates/register.html
- [X] T023 [US3] Ensure registration remains accessible while signed in (no auth-block redirect) in src/app.py

**Checkpoint**: All user stories are independently complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, consistency, and validation across all stories.

- [X] T024 [P] Harden registration error handling to avoid sensitive leakage in src/app.py
- [X] T025 [P] Refine registration constants/messages for maintainability in src/services/registration_service.py
- [X] T026 Align quickstart execution notes with implemented behavior in specs/005-user-registration/quickstart.md
- [X] T027 Run quickstart validation flow and record outcomes in specs/005-user-registration/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all user stories.
- **Phase 3 (US1)**: Depends on Phase 2.
- **Phase 4 (US2)**: Depends on Phase 2; can proceed after US1 or in parallel once shared files are coordinated.
- **Phase 5 (US3)**: Depends on Phase 2 and uses account creation outcomes from US1 for realistic verification.
- **Phase 6 (Polish)**: Depends on completion of target user stories.

### User Story Dependencies

- **US1 (P1)**: No dependency on other user stories; defines MVP.
- **US2 (P2)**: No hard dependency on US3; builds on foundational validation plumbing.
- **US3 (P3)**: Depends on account persistence path delivered by US1.

### Within Each User Story

- Service rules before route-handler mapping.
- Route-handler mapping before template rendering updates.
- Template behavior before polish updates.

---

## Parallel Opportunities

- Setup: `T003` and `T004` can run in parallel after `T002` is created.
- Foundational: `T006` and `T007` can run in parallel after `T005` starts.
- US1: `T012` and `T013` can run in parallel with `T011`.
- US2: `T019` can run in parallel with `T017`/`T018`.
- Polish: `T024` and `T025` can run in parallel.

---

## Parallel Example: User Story 1

```bash
# Parallel UI updates once POST success path is in place:
Task: T012 [US1] Add Register navigation link to shared header in src/templates/base.html
Task: T013 [US1] Add registration success banner handling on home page in src/templates/home.html
```

## Parallel Example: User Story 2

```bash
# Parallel UX support while backend validation mapping is underway:
Task: T019 [US2] Add validation error-state styling in src/static/styles.css
Task: T018 [US2] Render field-level error messages and preserve non-sensitive input in src/templates/register.html
```

## Parallel Example: User Story 3

```bash
# Parallelize duplicate handling logic and user guidance updates:
Task: T020 [US3] Implement duplicate-email lookup helper in src/services/registration_service.py
Task: T022 [US3] Render duplicate-email guidance on registration form in src/templates/register.html
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate successful registration end-to-end before adding more scope.

### Incremental Delivery

1. Deliver US1 (account creation and activation).
2. Deliver US2 (validation and user feedback hardening).
3. Deliver US3 (duplicate-email handling and signed-in behavior confirmation).
4. Finish with Polish phase.

### Parallel Team Strategy

1. Team completes Setup + Foundational together.
2. Split by story focus:
   - Dev A: US1 route and persistence flow
   - Dev B: US2 validation + UX feedback
   - Dev C: US3 duplicate/email conflict behavior
3. Rejoin for Phase 6 polish and quickstart verification.
