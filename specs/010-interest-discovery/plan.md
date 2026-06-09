# Implementation Plan: Interest-Based Discover

**Branch**: `010-create-interest-discovery` | **Date**: 2026-06-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/010-interest-discovery/spec.md`

## Summary

Extend the authenticated Discover flow to produce deterministic interest-based defaults that use OR matching, relevance-first then recency ranking, and sparse-result backfill to a fixed minimum count, while preserving strict account isolation and onboarding prerequisites.

## Technical Context

**Language/Version**: Python 3.x  
**Primary Dependencies**: Flask, Flask-Login, sqlite3 (stdlib), arxiv client wrapper, pytest  
**Storage**: SQLite (`user_interest_preferences`, `user_interest_selections`, `interest_topics`) with existing app DB helpers in `src/services/db.py`  
**Testing**: pytest unit + integration tests via Flask test client  
**Target Platform**: Server-rendered Flask web app on local dev and WSGI-compatible runtime  
**Project Type**: Single-project web application  
**Performance Goals**: Align with spec: default Discover first result render under 2s for 90% sessions, updated interests reflected by next Discover load, and zero cross-user leakage in validation tests  
**Constraints**: Authenticated-only discover personalization, minimum 3 effective interests, automatic retired-interest reconciliation + default auto-fill, OR eligibility with relevance-first/recency-second ordering, sparse-result backfill behavior  
**Scale/Scope**: Existing single-node app and current user base; synchronous request path over bounded page-size result sets (default limit 10)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design | Post-Design |
|-----------|------------|-------------|
| I. Code Quality & Maintainability | PASS - feature can be delivered with route orchestration + service helper boundaries and focused test expansion | PASS - research, data model, and contract artifacts define explicit invariants, ownership boundaries, and testable behavior |
| II. User Experience Consistency | PASS - behavior extends existing auth/onboarding/discover journey with predictable redirects and messaging | PASS - quickstart and contract define consistent empty/sparse/default states and visible active-interest context |
| III. Performance Requirements | PASS - spec includes measurable response/reflection targets; implementation can reuse bounded fetch size and deterministic ranking | PASS - design includes fixed minimum-result backfill and constrained ordering rules suitable for stable latency |

**Gate result**: PASS. No constitutional violations requiring exceptions.

## Project Structure

### Documentation (this feature)

```text
specs/010-interest-discovery/
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
├── app.py                              # MODIFY: discover default query/ranking/backfill orchestration and active-interest context
├── services/
│   ├── db.py                           # MODIFY/VERIFY: effective-interest reconciliation helpers and default-interest retrieval
│   └── discovery_service.py            # MODIFY: ranking and sparse-result backfill pipeline
├── templates/
│   ├── home.html                       # MODIFY: active interest context and sparse/backfill messaging
│   └── interests.html                  # VERIFY/MODIFY: clarity around minimum-interest requirement and updates
└── clients/
    └── arxiv_client.py                 # VERIFY: metadata needed for relevance ordering is available and stable

tests/
├── integration/
│   ├── test_discovery_flow.py          # MODIFY: OR default, ranking order, sparse backfill, and immediate-update reflection
│   └── test_login_flow.py              # VERIFY: onboarding gate remains intact for discovery routes
└── unit/
    ├── test_interest_preferences.py    # MODIFY: retired-interest removal + default auto-fill + minimum effective count
    └── test_source_clients.py          # VERIFY/MODIFY: source metadata compatibility with ranking criteria
```

**Structure Decision**: Continue within the existing single Flask project. Keep policy decisions in `src/app.py`, reusable reconciliation/persistence utilities in `src/services/db.py`, and ranking/backfill mechanics in `src/services/discovery_service.py` so behavioral rules remain testable without spreading auth/session concerns across lower layers.

## Complexity Tracking

No constitutional violations requiring justification.
