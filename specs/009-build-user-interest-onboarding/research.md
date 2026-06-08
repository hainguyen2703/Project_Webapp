# Research: User Interest Selection Onboarding

**Feature**: 009-build-user-interest-onboarding  
**Date**: 2026-06-08  
**Status**: Complete

## Decision 1: Onboarding gate enforcement model

**Decision**: Enforce a hard post-auth onboarding gate for users without completed interest setup, including redirect from direct discovery routes.

**Rationale**: Clarifications require no skip path and consistent prerequisite enforcement before discovery personalization.

**Alternatives considered**:
- Allow one-time skip: rejected by clarification.
- Soft reminder banner: rejected because it cannot enforce completion requirements.

## Decision 2: Interest source and validation

**Decision**: Use only a predefined, product-managed interest catalog and reject custom free-text input.

**Rationale**: Supports consistent UX, deterministic validation, and cleaner analytics semantics.

**Alternatives considered**:
- Free-text only: rejected due to poor normalization and matching quality.
- Hybrid catalog + free-text: rejected by clarification.

## Decision 3: Preference matching strategy for defaults

**Decision**: Apply OR matching for discovery defaults (eligible if matching any selected interest) when user has no manual override.

**Rationale**: Clarified behavior and better coverage of relevant content while minimizing empty results.

**Alternatives considered**:
- AND matching: rejected as overly restrictive.
- Weighted ranking first: deferred as enhancement beyond current scope.

## Decision 4: Retired interest lifecycle handling

**Decision**: Automatically remove retired interests from user profiles and auto-fill missing slots with system defaults when profile count drops below minimum.

**Rationale**: Matches clarified behavior and keeps profiles compliant with minimum-interest constraints without forcing immediate user interruption.

**Alternatives considered**:
- Keep retired interests read-only: rejected by clarification.
- Force immediate re-selection: rejected by clarification.

## Decision 5: Persistence model and ownership

**Decision**: Persist user interest preferences as account-owned records in SQLite with strict user isolation.

**Rationale**: Existing architecture already uses SQLite for account-owned data; this provides durable preferences across sessions and clear ownership boundaries.

**Alternatives considered**:
- In-memory/session storage: rejected due to non-durability.
- Client-only local storage: rejected because ownership and server-side gating require authoritative backend state.

## Decision 6: Where to apply defaults in request flow

**Decision**: Apply onboarding/default-interest logic in route orchestration (`src/app.py`) before invoking discovery fetch logic.

**Rationale**: Keeps behavioral policy in route layer while reusing existing discovery service; avoids polluting lower-level clients with auth/session concerns.

**Alternatives considered**:
- Push logic entirely into discovery service: rejected because service lacks route-context semantics.
- Template-layer default composition: rejected because policy enforcement should happen before rendering.

## Residual Risks

- System default interests may bias discovery if catalog maintenance is poor; governance process should define default selection quality checks.
- Retired-interest auto-fill behavior needs transparent user messaging to avoid surprise preference changes.
- If catalog taxonomy changes frequently, migration and cache invalidation strategies may require later optimization.
