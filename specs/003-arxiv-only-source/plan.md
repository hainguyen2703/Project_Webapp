# Implementation Plan: Simplify to arXiv-Only Source

**Branch**: `003-arxiv-only-source` | **Date**: 2026-05-26 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/003-arxiv-only-source/spec.md`

## Summary

Simplify the paper discovery web app to use arXiv as the sole paper source. Delete `medium_client.py` and all Medium references from the backend. Remove the source-selection dropdown from `home.html`. Add a "Home" button to `base.html` that is visible on all pages and triggers a fresh arXiv fetch when clicked.

## Technical Context

**Language/Version**: Python 3.x / Flask 2.0+  
**Primary Dependencies**: Flask>=2.0, requests>=2.28, beautifulsoup4>=4.12, Jinja2 (bundled with Flask), pytest>=8.0  
**Storage**: In-memory dict (`LATEST_RESULTS`) — no persistent storage  
**Testing**: pytest 8.0+  
**Target Platform**: WSGI-compatible web server (development: Flask dev server, port 8000)  
**Project Type**: Web application  
**Performance Goals**: N/A — simplification change; no new load paths introduced  
**Constraints**: No new infrastructure; all changes are within existing source files  
**Scale/Scope**: 6 files modified, 1 file deleted, 3 new spec artifacts

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design | Post-Design |
|-----------|------------|-------------|
| I. Code Quality & Maintainability | PASS — deletion removes dead code; test suite updated to remove Medium tests and add Home button coverage | PASS |
| II. User Experience Consistency | PASS — Home button follows existing link/button patterns in `base.html`; error states remain consistent; "Return to list" simplified | PASS |
| III. Performance Requirements | PASS — simplification only; removing Medium reduces potential outbound HTTP calls | PASS |

**Gate result**: All principles PASS. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/003-arxiv-only-source/
├── plan.md              ← This file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/
│   └── api-contract.md  ← Phase 1 output
└── tasks.md             ← Phase 2 output (/speckit.tasks — NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── app.py                         ← MODIFY: remove CONTENT_SOURCES, simplify LATEST_RESULTS, hardcode arxiv
├── clients/
│   ├── arxiv_client.py            ← KEEP (unchanged)
│   └── medium_client.py           ← DELETE
├── models/
│   ├── article.py                 ← KEEP (unchanged)
│   └── source.py                  ← KEEP (out of scope; not referenced in active code)
├── services/
│   ├── discovery_service.py       ← MODIFY: remove Medium import and elif branch
│   └── result_formatter.py        ← KEEP (unchanged)
├── static/
│   └── styles.css                 ← MODIFY: add .home-btn style if needed
└── templates/
    ├── base.html                  ← MODIFY: add Home button anchor to header
    ├── detail.html                ← MODIFY: simplify "Return to list" link (remove source param)
    └── home.html                  ← MODIFY: remove source <select> dropdown

tests/
├── integration/
│   └── test_discovery_flow.py     ← MODIFY: replace Medium error test; add Home button visibility test
└── unit/
    ├── test_models.py             ← KEEP (unchanged)
    └── test_source_clients.py     ← MODIFY: remove Medium client import and test function
```

**Structure Decision**: Single web application. All changes are within the existing `src/` and `tests/` directories. No new directories are introduced.
