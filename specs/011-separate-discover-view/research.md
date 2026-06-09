# Research: Separate Discover View

**Feature**: 011-separate-discover-view  
**Date**: 2026-06-09  
**Status**: Complete

## Decision 1: Route split and ownership

**Decision**: Keep Home at `/` and add Discover at `/discover`.

**Rationale**: Aligns with clarified intent, keeps canonical landing route stable, and creates explicit information architecture.

**Alternatives considered**:
- Keep Discover at `/` and move Home elsewhere: rejected by clarification.
- Single route with mode switch: rejected because it weakens route semantics.

## Decision 2: Access policy for `/discover`

**Decision**: Require authentication for `/discover`; unauthenticated users are redirected to login.

**Rationale**: Preserves current prerequisite and personalization boundaries while minimizing anonymous route ambiguity.

**Alternatives considered**:
- Anonymous access with limited mode: rejected by clarification.
- Hidden without redirect semantics: rejected due to weaker user recovery path.

## Decision 3: Behavior parity across Home and Discover

**Decision**: Keep discovery search and result rendering functionally identical on both `/` and `/discover`.

**Rationale**: Clarified requirement prioritizes parity over differentiation for this feature increment.

**Alternatives considered**:
- Move discovery only to `/discover`: rejected by clarification.
- Keep partial feature split: rejected due to inconsistent user expectations.

## Decision 4: State synchronization scope

**Decision**: Synchronize query/filter state across Home and Discover only within the same active browser session and not via URL parameters.

**Rationale**: Meets clarified behavior while avoiding URL complexity and shared-link state leakage.

**Alternatives considered**:
- URL-parameter synchronization: rejected by clarification.
- Fully independent state per view: rejected by clarification.

## Decision 5: Post-login navigation target

**Decision**: After successful login, land users on Home (`/`) and require explicit navigation to Discover.

**Rationale**: Keeps existing login flow stable and consistent with the new split-view model.

**Alternatives considered**:
- Always land on `/discover`: rejected by clarification.
- Return-to-last-route behavior as default: rejected by clarification.

## Decision 6: Rendering strategy

**Decision**: Use shared rendering helpers/context assembly for Home and Discover to avoid duplicated business logic while allowing route-specific page identity.

**Rationale**: Maintains parity guarantees and reduces divergence risk over time.

**Alternatives considered**:
- Duplicate templates and controller logic per route: rejected due to maintainability risk.
- Full template merge with no route identity: rejected because active navigation context must remain explicit.

## Residual Risks

- Keeping identical behavior on both views can reduce perceived distinction if navigation cues are weak.
- Session-scoped state sync requires careful reset behavior on logout/session expiry.
- Future divergence requests between Home and Discover may require refactoring shared render contracts.
