# Research: Standardize arXiv Discovery Source

**Feature**: 007-rework-arxiv-lib  
**Date**: 2026-06-04  
**Status**: Complete

## Decision 1: arXiv integration mechanism

**Decision**: Replace direct XML-over-HTTP parsing in discovery with the official Python `arxiv` library as the retrieval client.

**Rationale**: The feature goal is explicitly to rework with the arXiv Python library. The library provides typed result handling, query composition, and stable abstractions that reduce parser fragility and simplify maintenance.

**Alternatives considered**:
- Keep `requests` + manual XML parsing: rejected due to higher parsing risk and maintenance overhead.
- Use an unrelated third-party wrapper: rejected to avoid extra abstraction layers and unclear long-term support.

## Decision 2: Canonical paper identifier

**Decision**: Use arXiv ID as the canonical identifier across discovery, detail, and favorites eligibility checks.

**Rationale**: Clarification established arXiv ID as the authoritative key. This supports deterministic deduplication and stable record matching independent of URL formatting.

**Alternatives considered**:
- Use canonical link as identifier: rejected due to potential URL representation drift.
- Use both with no authority rule: rejected due to ambiguity in conflict handling.

## Decision 3: Timeout and fallback behavior

**Decision**: Enforce a 4-second retrieval timeout and return a retry-ready failure state when timeout occurs.

**Rationale**: This directly satisfies clarified requirement FR-013 and aligns with SC-001/SC-005 responsiveness targets.

**Alternatives considered**:
- Longer timeout (10s): rejected due to poorer user responsiveness.
- No timeout: rejected because it can stall user flow indefinitely.

## Decision 4: Malformed required-field handling

**Decision**: Exclude records with malformed required fields while continuing to return valid records.

**Rationale**: This preserves data quality guarantees for displayed content (SC-002) while avoiding full-response failure for partial source corruption.

**Alternatives considered**:
- Show malformed records as-is: rejected because it violates required-content quality.
- Fail entire response on one malformed record: rejected because it harms availability and user value.

## Decision 5: Where to enforce normalization and filtering

**Decision**: Keep source retrieval in `src/clients/arxiv_client.py`, enforce normalization and required-field filtering before final result formatting in discovery-service flow.

**Rationale**: This keeps responsibilities clear: client fetches source entries, service layer enforces domain rules, formatter returns presentation payload.

**Alternatives considered**:
- Put all filtering inside templates: rejected because UI should not enforce source-data correctness.
- Put filtering only in model serialization: rejected because invalid records should be excluded before response assembly.

## Implementation Notes

- Implemented retrieval via `arxiv.Search` and `arxiv.Client` in `src/clients/arxiv_client.py`.
- Implemented canonical ID extraction helper and canonical URL construction in the client.
- Implemented 4-second timeout mapping and malformed-record filtering in `src/services/discovery_service.py`.
- Updated detail/favorites lookup to use canonical arXiv IDs while preserving backward-compatible ID normalization in `src/app.py`.

## Residual Risks

- arXiv upstream API or package-level schema changes could alter field availability; malformed-record filtering mitigates UI impact but may increase empty-result frequency.
- Canonical ID extraction currently supports common modern and legacy arXiv formats; rare non-standard identifiers may still be excluded as malformed.
