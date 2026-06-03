# Implementation Plan: Standardize arXiv Discovery Source

**Branch**: `007-rework-arxiv-lib` | **Date**: 2026-06-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/007-rework-arxiv-lib/spec.md`

## Summary

Rework discovery fetching to use the Python `arxiv` library while preserving current user workflows, enforcing canonical arXiv-ID based records, and implementing strict timeout and malformed-record filtering behavior required by the clarified specification.

## Technical Context

**Language/Version**: Python 3.x  
**Primary Dependencies**: Flask, Flask-Login, pytest, Python `arxiv` library, existing `requests` dependency retained for unrelated code paths  
**Storage**: In-memory result/favorites stores and SQLite auth/registration storage (unchanged by this feature)  
**Testing**: pytest unit + integration tests using Flask test client and source-client mocking  
**Target Platform**: Server-rendered Flask web app running locally or WSGI-hosted Python runtime  
**Project Type**: Web application (single backend project)  
**Performance Goals**: Discovery success or user-visible fallback in <=4 seconds for 95% of requests; deterministic retry availability after timeout  
**Constraints**: arXiv is the only source; canonical identifier must be arXiv ID; malformed required-field records must be excluded; existing routes/workflows must remain stable  
**Scale/Scope**: Current app scale (single deployment), top-N discovery lists, and existing integration test breadth for discovery/detail/favorites flows

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design | Post-Design |
|-----------|------------|-------------|
| I. Code Quality & Maintainability | PASS - Clear separation between source client, service normalization, and formatter outputs | PASS - Research/data model/contracts define explicit validation boundaries and test targets |
| II. User Experience Consistency | PASS - Existing home/detail/favorites journeys remain unchanged while data quality improves | PASS - Contract preserves route behavior and defines consistent error/no-result/retry states |
| III. Performance Requirements | PASS - 4-second timeout and retry behavior are explicit non-functional requirements | PASS - Quickstart validation includes timeout and malformed-data scenarios with measurable outcomes |

**Gate result**: PASS. No constitutional violations requiring exception tracking.

## Project Structure

### Documentation (this feature)

```text
specs/007-rework-arxiv-lib/
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
├── clients/
│   └── arxiv_client.py              # MODIFY: use arxiv Python library and canonical ID extraction
├── services/
│   ├── discovery_service.py         # MODIFY: timeout/fallback and malformed required-field filtering
│   └── result_formatter.py          # VERIFY: payload shape and fetched_at behavior
├── models/
│   └── article.py                   # VERIFY/MODIFY: required-field validation and canonical-id expectations
├── app.py                           # VERIFY/MODIFY: detail lookup compatibility with canonical IDs
└── templates/
    ├── home.html                    # VERIFY: retry/no-result messaging compatibility
    └── detail.html                  # VERIFY: required content rendering

tests/
├── unit/
│   └── test_source_clients.py       # MODIFY: client behavior with arxiv lib + canonical IDs
└── integration/
    └── test_discovery_flow.py       # MODIFY: success, timeout retry state, malformed filtering behavior
```

**Structure Decision**: Continue with the existing single-project Flask architecture. Keep integration logic in `src/clients` and enforce feature rules in `src/services` so contracts remain stable to templates and routes.

## Complexity Tracking

No constitution violations requiring justification.

## Implementation Notes

- Replaced direct XML parsing with Python `arxiv` library retrieval flow in `src/clients/arxiv_client.py`.
- Introduced canonical arXiv ID extraction and canonical URL normalization for all discovery records.
- Enforced required-field filtering and 4-second timeout mapping in `src/services/discovery_service.py`.
- Updated detail and favourites ID lookup in `src/app.py` to normalize legacy URL-form IDs to canonical IDs.

## Verification Notes

- `python -m pytest tests/unit/test_source_clients.py tests/unit/test_models.py tests/integration/test_discovery_flow.py` -> pass
- `python -m pytest tests/` -> pass (38 tests)
