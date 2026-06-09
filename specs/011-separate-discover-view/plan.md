# Implementation Plan: Separate Discover View

**Branch**: `011-separate-discover-view` | **Date**: 2026-06-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-separate-discover-view/spec.md`

## Summary

Introduce a dedicated authenticated Discover route at `/discover` while keeping Home at `/`, preserving identical search/result behavior across both views, enforcing session-scoped state sync (not URL-based), and maintaining current onboarding/personalization prerequisites.

## Technical Context

**Language/Version**: Python 3.x  
**Primary Dependencies**: Flask, Flask-Login, sqlite3 (stdlib), pytest  
**Storage**: SQLite-backed auth and preference state; server-side session for in-session Home/Discover state sync  
**Testing**: pytest integration and unit suites via Flask test client  
**Target Platform**: Server-rendered Flask app (local dev + WSGI deployment)  
**Project Type**: Single-project web application  
**Performance Goals**: Preserve existing discovery response behavior with no material latency regression; maintain current regression-suite pass rates for routing/auth/discovery flows  
**Constraints**: `/discover` requires authentication; login lands on `/`; Home and Discover must expose functionally identical search/results; session-only state sync; no URL-param dependency for cross-view state transfer  
**Scale/Scope**: Existing app scale and route surface; one additional top-level route and shared rendering behavior

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design | Post-Design |
|-----------|------------|-------------|
| I. Code Quality & Maintainability | PASS - route separation can be delivered via reusable helpers and minimal duplication | PASS - plan/data-model/contracts preserve clear responsibilities for routing, view context, and state sync |
| II. User Experience Consistency | PASS - explicit Home/Discover split with active-state cues improves predictability | PASS - quickstart and contract define consistent navigation, access handling, and identical discovery behavior across both views |
| III. Performance Requirements | PASS - implementation reuses existing discovery pipeline and bounded result handling | PASS - design avoids extra round-trips and keeps state sync session-local, minimizing overhead |

**Gate result**: PASS. No constitutional violations requiring exceptions.

## Project Structure

### Documentation (this feature)

```text
specs/011-separate-discover-view/
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
├── app.py                              # MODIFY: add /discover route, shared search/result orchestration, session-scoped cross-view state
├── templates/
│   ├── base.html                       # MODIFY: Home/Discover navigation cues + active location indicator
│   ├── home.html                       # MODIFY: shared discovery UI compatibility and state usage
│   └── discover.html                   # ADD or derive-from-home template for dedicated Discover route
├── services/
│   └── discovery_service.py            # VERIFY: no behavioral divergence between Home and Discover fetch paths
└── services/db.py                      # VERIFY: prerequisite/auth logic remains consistent for /discover

tests/
├── integration/
│   ├── test_discovery_flow.py          # MODIFY: /discover route access and behavior parity with /
│   └── test_login_flow.py              # MODIFY: post-login landing remains /
└── unit/
    └── test_models.py                  # VERIFY: no model contract regression from view split
```

**Structure Decision**: Keep the single Flask project structure and implement route separation in `src/app.py` with shared helper-driven rendering so Home and Discover behavior stay identical while routing, auth gating, and navigation semantics remain explicit and testable.

## Complexity Tracking

No constitutional violations requiring justification.
