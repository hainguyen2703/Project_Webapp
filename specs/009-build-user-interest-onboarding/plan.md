# Implementation Plan: User Interest Selection Onboarding

**Branch**: `009-build-user-interest-onboarding` | **Date**: 2026-06-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-build-user-interest-onboarding/spec.md`

## Summary

Introduce mandatory post-auth onboarding for interest selection, persist account-owned interest preferences from a predefined catalog, apply OR-based discovery defaults from saved interests, and enforce lifecycle rules for retired interests and account deletion.

## Technical Context

**Language/Version**: Python 3.x  
**Primary Dependencies**: Flask, Flask-Login, sqlite3 (stdlib), pytest  
**Storage**: SQLite for user accounts and user interest preferences; in-memory discovery result cache remains for request/session-level data  
**Testing**: pytest unit + integration tests using Flask test client and DB fixtures  
**Target Platform**: Server-rendered Flask web app running on local dev and WSGI-compatible deployment targets  
**Project Type**: Single-project web application  
**Performance Goals**: 95% onboarding completion under 2 minutes (spec SC-001); preference save success >=99% first attempt (SC-002); default discovery personalization applied on every non-overridden onboarded session (SC-004)  
**Constraints**: Authenticated-only onboarding/management, no free-text interests, no onboarding skip, OR matching for defaults, automatic retired-interest removal and fallback defaults when below minimum  
**Scale/Scope**: Existing app scale with account-backed preferences for all authenticated users and small catalog size suitable for synchronous page render paths

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design | Post-Design |
|-----------|------------|-------------|
| I. Code Quality & Maintainability | PASS - clear separation feasible across route logic, DB helpers, and templates with test coverage additions | PASS - data model/contracts define boundaries and deterministic validation rules for onboarding and preferences |
| II. User Experience Consistency | PASS - onboarding gate and interest-management flows can be integrated into existing auth/discovery journey with predictable messaging | PASS - contracts and quickstart define consistent authenticated flow, validation feedback, and route behavior |
| III. Performance Requirements | PASS - measurable onboarding/save/default targets are present in spec and can be validated with integration tests | PASS - design uses bounded catalog and indexed preference retrieval to keep request cost predictable |

**Gate result**: PASS. No constitutional violations requiring exceptions.

## Project Structure

### Documentation (this feature)

```text
specs/009-build-user-interest-onboarding/
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
├── app.py                              # MODIFY: onboarding gate, interest save/update routes, discovery default injection
├── services/
│   ├── db.py                           # MODIFY: interest catalog, user preference persistence, retired-interest cleanup helpers
│   └── discovery_service.py            # VERIFY/MODIFY: support default query/filter input from selected interests
├── templates/
│   ├── base.html                       # MODIFY: link to interest management for authenticated users
│   ├── home.html                       # MODIFY: show interest-driven default discovery context
│   ├── onboarding_interests.html       # ADD: onboarding interest selection screen
│   └── interests.html                  # ADD: post-onboarding interest management screen
└── models/
    └── article.py                      # VERIFY: compatibility of interest-driven defaults with existing article rendering

tests/
├── integration/
│   ├── test_login_flow.py              # MODIFY: onboarding gate behavior after auth
│   └── test_discovery_flow.py          # MODIFY: OR-based interest defaults and override behavior
└── unit/
    ├── test_auth_service.py            # VERIFY: no auth regressions from onboarding gate
    └── test_registration_service.py    # VERIFY/MODIFY: account deletion lifecycle with interest cleanup
```

**Structure Decision**: Continue with the existing single Flask project and extend current app/db modules. Keep persistence and validation in `src/services/db.py`, orchestrate flow in `src/app.py`, and add dedicated templates for onboarding and interest management to preserve UX consistency.

## Complexity Tracking

No constitutional violations requiring justification.
