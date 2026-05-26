# Implementation Plan: Hamburger Menu with Favourites

**Branch**: `004-hamburger-favourites` | **Date**: 2026-05-26 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/004-hamburger-favourites/spec.md`

## Summary

Add a server-side in-memory favourites system to the paper discovery app. Users save/remove papers via a heart button (♡/♥) on the detail page using POST-Redirect-GET. A CSS-only hamburger menu (☰) in the header on all pages links to a new `/favourites` route that lists saved papers in reverse chronological order with per-item × remove controls. The detail route gains a fallback lookup from the favourites store so linked papers remain viewable even after search results change.

## Technical Context

**Language/Version**: Python 3.x / Flask 2.0+  
**Primary Dependencies**: Flask>=2.0, requests>=2.28, beautifulsoup4>=4.12, Jinja2 (bundled), pytest>=8.0; `secrets` and `os` from stdlib  
**Storage**: In-memory dict `FAVOURITES_STORE` (server-side, keyed by UUID from `session['user_id']`); Flask signed-cookie session (UUID only — no large payloads in cookie)  
**Testing**: pytest 8.0+  
**Target Platform**: WSGI-compatible web server (development: Flask dev server, port 8000)  
**Project Type**: Web application  
**Performance Goals**: No network calls for favourite toggle/remove/listing; in-memory lookups only  
**Constraints**: Zero new pip dependencies; CSS-only hamburger (no JavaScript); POST-Redirect-GET for all state-changing actions  
**Scale/Scope**: 5 files modified, 1 new template, 1 new spec artifacts directory; ~6 new tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design | Post-Design |
|-----------|------------|-------------|
| I. Code Quality & Maintainability | PASS — POST-Redirect-GET prevents resubmission; secret key via env var; all new routes tested; no dead code | PASS |
| II. User Experience Consistency | PASS — heart button and × remove styled to match existing button/link patterns; hamburger CSS-only consistent with server-rendered app; Favourites page uses same card-based layout | PASS |
| III. Performance Requirements | PASS — all favourites operations are pure in-memory; zero external network calls for toggle/remove/list | PASS |

**Gate result**: All principles PASS. No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/004-hamburger-favourites/
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
├── app.py                         ← MODIFY: add FAVOURITES_STORE, secret_key, 3 new routes,
│                                             update item_detail with favourites fallback
├── clients/
│   └── arxiv_client.py            ← KEEP (unchanged)
├── models/
│   └── article.py                 ← KEEP (unchanged)
├── services/
│   └── discovery_service.py       ← KEEP (unchanged)
├── static/
│   └── styles.css                 ← MODIFY: add hamburger, heart button, favourites page styles
└── templates/
    ├── base.html                  ← MODIFY: add hamburger checkbox toggle + nav with Favourites link
    ├── detail.html                ← MODIFY: add heart form (POST to /favourite/toggle), pass is_favourite
    ├── favourites.html            ← NEW: favourites list with detail links and × remove forms
    └── home.html                  ← KEEP (unchanged)

tests/
└── integration/
    └── test_discovery_flow.py     ← MODIFY: add 6 new test functions for favourites flows
```

**Structure Decision**: Single web application. All changes are within existing `src/` and `tests/` directories. One new template file (`favourites.html`) is added.
