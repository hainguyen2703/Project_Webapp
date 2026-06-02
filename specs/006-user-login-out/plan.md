# Implementation Plan: User Login and Logout

**Branch**: `006-add-login-logout` | **Date**: 2026-06-03 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/006-user-login-out/spec.md`

## Summary

Implement login/logout for existing registered users using Flask-LoginManager on top of the current Flask app and SQLite user storage. The flow adds dedicated login/logout routes, session handling, invalid-attempt throttling, and robust signed-in/signed-out edge behavior per the accepted clarifications.

## Technical Context

**Language/Version**: Python 3.x with Flask 3.x  
**Primary Dependencies**: Flask, Flask-Login (LoginManager), Werkzeug security helpers, sqlite3, Jinja2 templates, pytest  
**Storage**: SQLite user account table (`src/data/app.db`) + session metadata for active login state  
**Testing**: pytest unit and integration tests with Flask test client  
**Target Platform**: WSGI web app on local/dev server (`python -m src.app`)  
**Project Type**: Server-rendered web application  
**Performance Goals**: Login verification p95 < 250 ms in local environment; logout response < 150 ms; no measurable slowdown to existing discovery endpoints  
**Constraints**: Must integrate with existing registration accounts, preserve existing pages/routes, enforce temporary throttling on repeated failed logins, block signed-out logout requests with 401/403, and support global logout invalidation semantics  
**Scale/Scope**: Single-app deployment baseline with up to 10k accounts and multi-session behavior tracked at app level

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design | Post-Design |
|-----------|------------|-------------|
| I. Code Quality & Maintainability | PASS - Design separates auth/session logic into focused services with explicit contracts and tests | PASS - Data model, contract, and quickstart define deterministic validation and error handling paths |
| II. User Experience Consistency | PASS - Login/logout pages and messages will follow existing template patterns and feedback style | PASS - Contracts specify consistent signed-in/signed-out behavior across edge cases |
| III. Performance Requirements | PASS - Login checks are single-row lookups plus hash verification; throttling state in memory | PASS - Targets and validation steps included in quickstart and test plan |

**Gate result**: PASS. No constitutional violations requiring exceptions.

## Project Structure

### Documentation (this feature)

```text
specs/006-user-login-out/
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
├── app.py                               # MODIFY: add login/logout routes and LoginManager wiring
├── services/
│   ├── auth_service.py                  # NEW: credential validation, throttling, and session helpers
│   ├── db.py                            # MODIFY: user lookup helpers for login integration
│   └── registration_service.py          # KEEP: existing account creation and hash behavior
├── models/
│   └── auth_user.py                     # NEW: Flask-Login user adapter for registered accounts
├── templates/
│   ├── base.html                        # MODIFY: login/logout navigation state
│   ├── home.html                        # MODIFY: auth status messaging hooks
│   └── login.html                       # NEW: login form and feedback
└── static/
    └── styles.css                       # MODIFY: login form and auth status styles

tests/
├── integration/
│   └── test_login_flow.py               # NEW: end-to-end login/logout/session behavior
└── unit/
    └── test_auth_service.py             # NEW: credential checks, throttling, and edge rules
```

**Structure Decision**: Keep the existing single-app structure and add a dedicated authentication service plus a lightweight `AuthUser` model for Flask-LoginManager integration. This minimizes impact on existing discovery and favourites features while enabling explicit test coverage.

## Complexity Tracking

No constitution violations requiring justification.
