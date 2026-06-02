# Implementation Plan: User Registration

**Branch**: `005-build-user-registration` | **Date**: 2026-06-02 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/005-user-registration/spec.md`

## Summary

Implement server-rendered user registration backed by SQLite, with password hashing via Werkzeug security helpers. The flow adds a new registration form and POST endpoint that validates required fields, enforces password policy, rejects leading/trailing whitespace in email, blocks duplicate emails, and treats rapid duplicate submissions as single-flight requests. Newly created accounts are active immediately, and registration remains available even when a user is already signed in.

## Technical Context

**Language/Version**: Python 3.x with Flask 2.x  
**Primary Dependencies**: Flask, Jinja2 templates, Werkzeug security (`generate_password_hash`, `check_password_hash`), sqlite3 (stdlib), pytest  
**Storage**: SQLite file database (`src/data/app.db`) with unique index on email and created-at audit fields  
**Testing**: pytest unit + integration tests via Flask test client  
**Target Platform**: WSGI-hosted web app (local dev on Flask server, port 8000)  
**Project Type**: Web application (single backend + server-rendered templates)  
**Performance Goals**: Registration POST median < 200 ms locally; p95 < 500 ms for validation and DB insert paths; complete successful registration in < 2 minutes user time (SC-001)  
**Constraints**: No new external services, no client-side framework, reject emails with leading/trailing whitespace, process only first in-flight submission per request token, keep behavior consistent with existing templates and styles  
**Scale/Scope**: Single-process local app baseline; design for at least 10k stored accounts with indexed uniqueness checks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design | Post-Design |
|-----------|------------|-------------|
| I. Code Quality & Maintainability | PASS - Plan adds isolated registration service + DB helper boundaries, explicit validation rules, and mandatory test coverage | PASS - Data model, contract, and quickstart define testable behaviors and failure paths |
| II. User Experience Consistency | PASS - Registration flow uses existing server-rendered patterns, explicit validation messaging, and predictable redirects | PASS - Contract and quickstart preserve consistent feedback states across success and error cases |
| III. Performance Requirements | PASS - SQLite indexed lookup + single insert path keeps latency bounded for registration checks | PASS - Performance goals and test scenarios included in plan artifacts |

**Gate result**: PASS. No constitutional violations requiring exceptions.

## Project Structure

### Documentation (this feature)

```text
specs/005-user-registration/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── app.py                              # MODIFY: add GET/POST /register and submission guard integration
├── data/
│   └── app.db                          # NEW: SQLite database file (runtime generated)
├── services/
│   ├── registration_service.py         # NEW: validation, duplicate detection, account creation
│   └── db.py                           # NEW: SQLite connection and schema bootstrap helpers
├── templates/
│   ├── base.html                       # MODIFY: navigation entry for Register
│   ├── home.html                       # MODIFY: optional success banner after registration
│   └── register.html                   # NEW: registration form + validation errors
└── static/
    └── styles.css                      # MODIFY: registration form and message styles

tests/
├── integration/
│   └── test_registration_flow.py       # NEW: end-to-end registration success/error flows
└── unit/
    └── test_registration_service.py    # NEW: password policy, whitespace, duplicate rules
```

**Structure Decision**: Keep a single Flask web app structure under `src/` and add focused service modules for DB and registration logic. This minimizes risk to existing discovery/favourites behavior while enabling isolated testing.

## Complexity Tracking

No constitution violations or exceptional complexity requiring justification.
