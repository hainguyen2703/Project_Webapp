# Implementation Plan: User Email Registration

**Branch**: `002-user-email-registration` | **Date**: 2026-05-14 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/002-user-email-registration/spec.md`

## Summary

Add email-based account registration to the Paper Discovery webapp. Users submit a Gmail address, password, and Privacy Policy consent via a new registration form. The system creates a pending account, sends a verification email containing a single-use token link, and activates the account on click. Pending accounts unverified after 24 hours are purged. The implementation adds Flask-SQLAlchemy (SQLite) for persistence and Flask-Mail for SMTP-based email delivery to the existing Flask codebase.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Flask≥2.0 (existing), Flask-SQLAlchemy≥3.0 (new), Flask-Mail≥0.9.1 (new), Werkzeug (bundled with Flask — password hashing)  
**Storage**: SQLite via Flask-SQLAlchemy (v1); schema: `UserAccount`, `VerificationToken`, `EmailNotification`  
**Testing**: pytest≥8.0 (existing)  
**Target Platform**: Desktop web browser (server: Python/Flask process)  
**Project Type**: Web application (server-rendered HTML templates)  
**Performance Goals**: Registration + verification flow completable in under 3 minutes (SC-001); verification email delivered within 2 minutes in 95% of cases (SC-003)  
**Constraints**: Desktop-only (no mobile); Gmail-only email domain (FR-002); no background task queue for v1  
**Scale/Scope**: v1 — small user base; SQLite sufficient; lazy pending-account purge acceptable

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

### Principle I — Code Quality & Maintainability
- **PASS**: New models (`UserAccount`, `VerificationToken`) will have unit tests covering validation rules. Registration service logic (domain check, duplicate detection, token generation) is isolated in `src/services/` and covered by targeted tests. Linting and static analysis apply to all new files.

### Principle II — User Experience Consistency
- **PASS**: Registration form uses the existing `base.html` template and shared `styles.css`. Field-level error messages follow the same feedback pattern used in the existing search/filter flows. The "Check your email" and verification confirmation pages are new but use the same base layout. No new design patterns introduced.

### Principle III — Performance Requirements
- **PASS**: SC-001 (< 3 min for full flow) and SC-003 (email within 2 min, 95%) are measurable performance criteria defined in the spec. SMTP send is synchronous but is expected to complete in < 2 seconds under normal SMTP latency. The lazy purge query is a lightweight indexed DELETE run at most once per registration attempt.

**Constitution verdict**: All principles satisfied. No violations to track.

## Project Structure

### Documentation (this feature)

```text
specs/002-user-email-registration/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── api-contract.md  # Phase 1 output
├── checklists/
│   └── requirements.md
├── spec.md
└── tasks.md             # Phase 2 output (/speckit.tasks — not yet created)
```

### Source Code (repository root)

```text
src/
├── app.py                          # Add: DB init, Mail init, register/verify/resend/check-email routes
├── models/
│   ├── article.py                  # Existing — unchanged
│   ├── source.py                   # Existing — unchanged
│   └── user.py                     # New: UserAccount, VerificationToken, EmailNotification models
├── services/
│   ├── __init__.py                 # Existing
│   ├── discovery_service.py        # Existing — unchanged
│   ├── result_formatter.py         # Existing — unchanged
│   └── registration_service.py     # New: registration, verification, resend, purge logic
├── templates/
│   ├── base.html                   # Existing — unchanged
│   ├── home.html                   # Existing — unchanged
│   ├── detail.html                 # Existing — unchanged
│   ├── register.html               # New: registration form
│   ├── check_email.html            # New: "Check your email" confirmation page
│   └── verify_result.html          # New: verification success / error / already-verified page
└── static/
    └── styles.css                  # Existing — extend with form & error styles if needed

tests/
├── unit/
│   ├── test_models.py              # Existing — extend with UserAccount/VerificationToken tests
│   ├── test_source_clients.py      # Existing — unchanged
│   └── test_registration_service.py  # New: unit tests for registration_service.py
└── integration/
    ├── test_discovery_flow.py      # Existing — unchanged
    └── test_registration_flow.py   # New: end-to-end register → verify flow tests
```

**Structure Decision**: Single-project web application layout. New code placed within the existing `src/` tree following the established `models/` + `services/` + `templates/` separation. No new top-level directories introduced.

## Complexity Tracking

*No constitution violations — table not required.*
