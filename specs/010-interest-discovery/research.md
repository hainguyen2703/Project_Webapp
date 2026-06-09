# Research: Interest-Based Discover

**Feature**: 010-interest-discovery  
**Date**: 2026-06-09  
**Status**: Complete

## Decision 1: Matching and ordering strategy

**Decision**: Use OR matching for eligibility and rank default Discover results by interest relevance first, then recency.

**Rationale**: OR eligibility ensures sufficient coverage for multi-interest users while relevance-first ordering keeps results aligned with intent and recency provides deterministic tie-breaking.

**Alternatives considered**:
- AND matching: rejected as too restrictive and likely to increase empty/sparse results.
- Recency-only ordering: rejected because it can bury the most interest-relevant content.
- Equal interleaving per interest: rejected due to added complexity and weaker overall relevance ranking.

## Decision 2: Sparse result strategy

**Decision**: Return direct interest matches first, then backfill with broader recent papers until a fixed minimum result count is reached.

**Rationale**: Preserves relevance while preventing a low-value empty or nearly empty Discover page for niche interests.

**Alternatives considered**:
- Show only direct matches and allow short/empty pages: rejected due to inconsistent user experience.
- Always fixed-ratio mixed feed: rejected because it can dilute relevance even when direct matches are abundant.

## Decision 3: Effective-interest lifecycle

**Decision**: Automatically remove retired interests from user context and auto-fill from system defaults when effective interest count falls below 3.

**Rationale**: Keeps user profiles valid without blocking discovery and aligns with previously accepted onboarding lifecycle behavior.

**Alternatives considered**:
- Block Discover until manual re-selection: rejected due to interruption and friction.
- Keep retired interests inert until user edits: rejected because it produces opaque behavior and unstable personalization quality.

## Decision 4: Update propagation timing

**Decision**: Apply saved interest updates immediately on the next Discover page load.

**Rationale**: Predictable behavior with no delay windows; improves user trust that preference changes took effect.

**Alternatives considered**:
- Delayed sync window (for example 5-15 minutes): rejected as confusing and harder to test.
- Session-bound refresh only: rejected because it delays expected feedback.

## Decision 5: Implementation boundary for ranking and backfill

**Decision**: Keep request policy in `src/app.py` and encapsulate ranking/backfill data processing in `src/services/discovery_service.py`.

**Rationale**: Route layer already owns auth and onboarding preconditions, while service layer is the right place for deterministic item ordering and fallback shaping.

**Alternatives considered**:
- Route-only implementation: rejected due to increasing endpoint complexity and reduced test isolation.
- Client-layer implementation in `arxiv_client`: rejected because source clients should stay source-focused, not user-personalization aware.

## Decision 6: Active interest transparency contract

**Decision**: Expose active effective interest keys in Discover render context so UI can explain why results are shown and when fallback/backfill occurred.

**Rationale**: Supports the transparency requirement and reduces mismatch between user expectation and displayed results.

**Alternatives considered**:
- No explicit context display: rejected due to lower trust and reduced diagnosability.
- Separate API call for active context only: rejected as unnecessary complexity for server-rendered page flow.

## Residual Risks

- Relevance scoring quality depends on metadata completeness from source results.
- Backfill can still surface lower-interest items; UI messaging must remain clear when backfill is active.
- If catalog churn increases, reconciliation frequency and cache behavior may need optimization beyond this scope.
