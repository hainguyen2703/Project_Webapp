# Implementation Plan: User-Owned Favourites

**Branch**: `008-user-owned-favourites` | **Date**: 2026-06-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-user-owned-favourites/spec.md`

## Summary

Move favourites from anonymous in-memory session ownership to authenticated user ownership backed by SQLite persistence, with strict per-user isolation, deterministic duplicate prevention via `(source, external_paper_id)`, unauthenticated route hiding/not-found behavior, and stable reverse-chronological display.

## Technical Context

**Language/Version**: Python 3.x  
**Primary Dependencies**: Flask, Flask-Login, sqlite3 (stdlib), pytest  
**Storage**: SQLite database for user accounts and persistent favourites; in-memory discovery result cache remains for current search session  
**Testing**: pytest unit + integration tests with Flask test client and database fixtures  
**Target Platform**: Server-rendered Flask app running on local/dev Python runtime and deployable WSGI-compatible environment  
**Project Type**: Web application (single backend project)  
**Performance Goals**: Favourite add/remove/list operations complete in <=500ms p95 in local baseline; post-login favourites page reachable and populated in <=10s (from spec SC-004)  
**Constraints**: Must enforce ownership isolation; unauthenticated users cannot discover favourites routes via navigation and direct access must return generic 404; immediate favourites deletion on account deletion  
**Scale/Scope**: Existing app scale with low-to-moderate per-user favourites cardinality (target <=500 favourites per user without UX degradation)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design | Post-Design |
|-----------|------------|-------------|
| I. Code Quality & Maintainability | PASS - clear service/db boundary can be preserved by introducing dedicated favourites persistence functions and tests | PASS - data model and contract define explicit ownership, uniqueness, and deletion semantics with testable behavior |
| II. User Experience Consistency | PASS - feature preserves existing discovery/detail flows while clarifying auth behavior for favourites access | PASS - quickstart and contract define consistent logged-in vs logged-out behavior, empty states, and recoverable navigation |
| III. Performance Requirements | PASS - explicit response-time targets and index-backed uniqueness model support bounded query/update costs | PASS - design includes indexed uniqueness and measurable validation scenarios for add/remove/list latency and login-to-favourites access |

**Gate result**: PASS. No constitution violations requiring exception tracking.

## Project Structure

### Documentation (this feature)

```text
specs/008-user-owned-favourites/
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
├── app.py                              # MODIFY: enforce auth gating + ownership-aware favourites routes
├── services/
│   ├── db.py                           # MODIFY: add favourites table schema and favourites CRUD helpers
│   └── auth_service.py                 # VERIFY: session/user identity lifecycle integration points
├── models/
│   └── article.py                      # VERIFY: paper fields used for persisted favourite payload
└── templates/
    ├── base.html                       # MODIFY: hide favourites navigation for unauthenticated users
    ├── detail.html                     # MODIFY: auth-aware favourite toggle affordance
    └── favourites.html                 # MODIFY: authenticated-only rendering and ordering checks

tests/
├── integration/
│   ├── test_discovery_flow.py          # MODIFY: adapt favourites flow assertions to authenticated ownership
│   └── test_login_flow.py              # MODIFY/ADD: verify favourites visibility and access control by auth state
└── unit/
    ├── test_registration_service.py    # VERIFY: account lifecycle assumptions
    └── test_auth_service.py            # VERIFY: session semantics used for ownership
```

**Structure Decision**: Keep the current single-project Flask structure. Implement favourites ownership and persistence in `src/services/db.py` and consume it from route handlers in `src/app.py` so templates remain thin and behavior is test-driven through existing unit/integration suites.

## Complexity Tracking

No constitution violations requiring justification.
