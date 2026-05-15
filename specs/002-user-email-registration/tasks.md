# Tasks: User Email Registration

**Input**: Design documents from `specs/002-user-email-registration/`  
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/api-contract.md ✅

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story.  
**Tests**: Not included (not explicitly requested in spec).

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which user story this task belongs to (US1 / US2 / US3)

---

## Phase 1: Setup

**Purpose**: Add new dependencies and configure infrastructure for the registration feature.

- [X] T001 Add `Flask-SQLAlchemy>=3.0` and `Flask-Mail>=0.9.1` to `requirements.txt`
- [X] T002 [P] Create `src/models/user.py` with empty module (placeholder for Phase 2 models)
- [X] T003 [P] Create `src/services/registration_service.py` with empty module (placeholder for Phase 2 logic)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database initialisation, mail configuration, and shared model definitions that ALL user stories depend on. No user story work can start until this phase is complete.

**⚠️ CRITICAL**: Phases 3–5 are blocked until this phase is complete.

- [X] T004 Implement `UserAccount` SQLAlchemy model in `src/models/user.py`
- [X] T005 Implement `VerificationToken` SQLAlchemy model in `src/models/user.py`
- [X] T006 [P] Implement `EmailNotification` SQLAlchemy model in `src/models/user.py`
- [X] T007 Initialise Flask-SQLAlchemy `db` instance and Flask-Mail `mail` instance in `src/app.py`
- [X] T008 Load `SECRET_KEY`, `DATABASE_URL`, `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER` from environment variables in `src/app.py`
- [X] T009 Implement `_purge_expired_pending_accounts(db_session)` utility in `src/services/registration_service.py`

**Checkpoint**: Database schema created, mail configured, purge utility ready — all user story work can now begin.

---

## Phase 3: User Story 1 — Register a new account with email (Priority: P1) 🎯 MVP

**Goal**: A new visitor can fill in the registration form, receive a verification email, click the link, and have their account activated.

**Independent Test**: Navigate to `/register`, submit a valid `@gmail.com` address + password + checked consent checkbox → redirected to `/check-email` → click verification link in email → see success confirmation page. Account `status` is `'active'` in the database.

### Implementation for User Story 1

- [X] T010 [US1] Implement `register_user(email, password, consent_at)` in `src/services/registration_service.py`
- [X] T011 [US1] Implement `send_verification_email(user, token, mail)` in `src/services/registration_service.py`
- [X] T012 [US1] Implement `verify_account(token_value, db_session)` in `src/services/registration_service.py`
- [X] T013 [P] [US1] Create `GET /register` route in `src/app.py`
- [X] T014 [US1] Create `POST /register` route in `src/app.py`
- [X] T015 [P] [US1] Create `GET /verify/<token>` route in `src/app.py`
- [X] T016 [P] [US1] Create `src/templates/register.html`
- [X] T017 [P] [US1] Create `src/templates/verify_result.html`
- [X] T018 [US1] Extend `src/static/styles.css` with form layout styles and field-level error message styles

**Checkpoint**: User Story 1 fully functional. A visitor can register, receive a verification email, and activate their account end-to-end.

---

## Phase 4: User Story 2 — Receive and act on the verification email (Priority: P2)

**Goal**: The verification email flow handles all link states: valid activation, expired link with resend, and already-used link — all with appropriate feedback to the user.

**Independent Test**: (a) Click a fresh verification link → account activates and success page shown. (b) Click an expired link (>24 h old) → expiry message and resend option shown. (c) Click an already-used link → "already verified" message shown. All three states render correctly without crashing.

### Implementation for User Story 2

- [X] T019 [US2] Implement `resend_verification(registration_id, db_session, mail)` in `src/services/registration_service.py`
- [X] T020 [US2] Create `GET /check-email` route in `src/app.py`
- [X] T021 [US2] Create `POST /resend-verification` route in `src/app.py`
- [X] T022 [P] [US2] Create `src/templates/check_email.html`

**Checkpoint**: User Story 2 fully functional. All verification link states and resend scenarios work correctly.

---

## Phase 5: User Story 3 — Receive meaningful feedback on invalid input (Priority: P3)

**Goal**: The registration form provides descriptive, field-level error messages for every invalid or incomplete input scenario without clearing valid fields.

**Independent Test**: Submit the registration form with: (a) blank email → email required error; (b) malformed email → format error; (c) non-Gmail domain → Gmail-only error; (d) short password → length/complexity error; (e) unchecked consent checkbox → consent required error. In each case only the relevant field shows an error and other entered values are preserved (FR-009).

### Implementation for User Story 3

- [X] T023 [US3] Add `validate_registration_input(email, password, consent)` function in `src/services/registration_service.py`
- [X] T024 [US3] Update `POST /register` route in `src/app.py` to call `validate_registration_input()`
- [X] T025 [US3] Update `src/templates/register.html` to render field-level error spans and re-populate email value on re-render

**Checkpoint**: All five invalid-input scenarios produce visible, field-specific error messages without full page reload or data loss (SC-005).

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, requirements validation, and quickstart verification.

- [X] T026 [P] Add `UserAccount` and `VerificationToken` unit tests to `tests/unit/test_models.py`
- [X] T027 [P] Create `tests/unit/test_registration_service.py`
- [X] T028 Create `tests/integration/test_registration_flow.py`
- [X] T029 Run `quickstart.md` validation — 38/38 tests pass, all success criteria confirmed
- [X] T030 [P] Update `requirements.txt` final version and verify `pip install -r requirements.txt` succeeds cleanly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — **BLOCKS phases 3–5**
- **Phase 3 (US1)**: Depends on Phase 2 — no dependency on US2 or US3
- **Phase 4 (US2)**: Depends on Phase 2 — US2 resend logic builds on US1 service functions (T010–T012); start after Phase 3 checkpoint
- **Phase 5 (US3)**: Depends on Phase 2 — validation logic is additive to US1 routes; start after Phase 3 checkpoint
- **Phase 6 (Polish)**: Depends on Phases 3–5 complete

### User Story Dependencies

- **US1 (P1)**: Independent after Phase 2 — core registration + verification path
- **US2 (P2)**: Integrates with US1 service layer (reuses `send_verification_email`); independently testable via the three link-state scenarios
- **US3 (P3)**: Additive to US1 form and route; independently testable via form validation scenarios

### Within Each User Story

- Service functions (T010–T012, T019, T023) before routes (T013–T015, T020–T021, T024)
- Routes before templates (T016–T017, T022, T025)
- Templates before CSS (T018)

### Parallel Opportunities

Within Phase 2:
- T004, T005, T006 can run in parallel (different models in same file — coordinate merge)
- T007, T008 can start after T004–T006

Within Phase 3:
- T013 (GET /register) and T016 (register.html) can be built in parallel with T010–T012 (service layer)
- T015 (GET /verify) and T017 (verify_result.html) can be built in parallel

Within Phase 6:
- T026, T027, T028 can run in parallel (different test files)
- T030 can run in parallel with tests

---

## Parallel Execution Example: Phase 3 (US1)

```
          T010 register_user()    ──────────────────────────────────┐
          T011 send_verification_email()  ──────────────────────────┤
          T012 verify_account()   ──────────────────────────────────┤
[Phase 2] ──▶ T013 GET /register (parallel) ──────────────────────▶ T014 POST /register ──▶ T018 CSS
          T015 GET /verify (parallel) ──────────────────────────────┘
          T016 register.html (parallel with T013) ─────────────────▶ T014 POST /register
          T017 verify_result.html (parallel with T015) ─────────────┘
```

---

## Implementation Strategy

**MVP Scope (Phase 1 + 2 + 3)**: Delivers User Story 1 — the complete register → verify flow. This is a working, independently demonstrable product increment.

**Increment 2 (+ Phase 4)**: Adds User Story 2 — full resend and link-state handling. Addresses email delivery edge cases.

**Increment 3 (+ Phase 5)**: Adds User Story 3 — polished field-level validation. Reduces form abandonment.

**Full delivery (+ Phase 6)**: Tests, quickstart validation, and final requirements check.
