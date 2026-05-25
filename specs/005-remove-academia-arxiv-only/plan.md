# Implementation Plan: Remove Academia.edu — arXiv Only

**Branch**: `005-remove-academia-arxiv-only` | **Date**: 2026-05-25 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/005-remove-academia-arxiv-only/spec.md`

## Summary

Remove the Academia.edu integration entirely: delete `academia_client.py`, strip the `academia` branch from the discovery service, remove the `CONTENT_SOURCES` list and source-selector dropdown from the UI, simplify all three routes (`/`, `/api/listings`, `/detail/<id>`) to be source-agnostic (always arXiv), and update the integration and unit test suite to reflect the new single-source reality.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: Flask 3.1.3, requests, beautifulsoup4, pytest 9.0.3, Flask-SQLAlchemy, Flask-Mail  
**Storage**: SQLite via Flask-SQLAlchemy (user registration only — no source data persisted)  
**Testing**: pytest  
**Target Platform**: Local development server (Flask built-in)  
**Project Type**: Web application (Flask, server-rendered Jinja2 templates)  
**Performance Goals**: N/A — this feature removes code; no new latency budget  
**Constraints**: All 49 existing tests must pass after changes; no stack traces exposed to users  
**Scale/Scope**: Small single-file Flask app; ~5 source files touched, ~3 test files touched

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|---|---|---|
| I. Code Quality & Maintainability | ✓ PASS | Dead code (academia client, CONTENT_SOURCES, unused imports) removed; pytest suite retained and updated |
| II. User Experience Consistency | ✓ PASS | Source selector removed consistently across all templates; error/retry flows preserved; detail return link updated |
| III. Performance Requirements | ✓ PASS | Only removing code; no new latency introduced; no performance regression possible |

**Gate result: PASS — proceed to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/005-remove-academia-arxiv-only/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/
│   └── api-contract.md  ← Phase 1 output
└── tasks.md             ← Phase 2 output (/speckit.tasks)
```

### Source Code (files changed by this feature)

```text
src/
├── app.py                           MODIFIED  — routes simplified, CONTENT_SOURCES removed
├── clients/
│   └── academia_client.py           DELETED
├── services/
│   └── discovery_service.py         MODIFIED  — academia import + branch removed
└── templates/
    ├── home.html                    MODIFIED  — source selector removed
    └── detail.html                  MODIFIED  — source param removed from return link

tests/
├── integration/
│   └── test_discovery_flow.py       MODIFIED  — test assertions updated for new routes
└── unit/
    └── test_source_clients.py       MODIFIED  — academia fixture + test removed
```

**Unchanged** (must not be modified):
- `src/models/source.py` — `ContentSource` dataclass retained as-is
- `src/clients/arxiv_client.py`
- `src/services/result_formatter.py`
- `src/templates/base.html`, `register.html`, `check_email.html`, `verify_result.html`
- `tests/integration/test_nav_dropdown.py`
- `tests/integration/test_registration_flow.py`
- `tests/unit/test_models.py`
- `tests/unit/test_registration_service.py`
