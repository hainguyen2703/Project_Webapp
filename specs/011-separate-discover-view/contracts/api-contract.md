# API Contract: Separate Discover View (v1)

**Feature**: 011-separate-discover-view  
**Date**: 2026-06-09

## Scope

Defines externally observable route behavior for Home (`/`) and Discover (`/discover`) separation while preserving identical discovery search/result behavior and session-scoped state synchronization.

## Route: GET /

Home route remains canonical landing view.

### Behavior

- Always reachable as Home view entry.
- Supports existing discovery search/results behavior identical to `/discover` when search/fetch is invoked.
- Participates in session-scoped query/filter synchronization with `/discover`.

## Route: GET /discover

Dedicated Discover route.

### Auth behavior

- Unauthenticated users: redirect to login.
- Authenticated users: return Discover view.

### Discover behavior parity

- Search controls and result rendering are functionally identical to `/`.
- Manual search override and default personalization semantics remain unchanged.
- Sparse-result/empty-result messaging semantics remain unchanged.

## Route: POST /login (existing)

### Post-login destination

- On successful login, redirect target is Home (`/`) regardless of Discover separation.

## Session state synchronization contract

- Home and Discover share query/filter state only within the same browser session.
- URL parameters are not required for cross-view state transfer.
- Shared links do not carry synchronized session state to other browser sessions.

## Navigation state contract

- UI must indicate active location (`Home` or `Discover`) clearly.
- Navigating between Home and Discover must not mislabel current location.

## Compatibility constraints

- Existing discovery payload shape remains unchanged.
- Existing onboarding/personalization prerequisite checks remain intact.
- Existing favorites and detail flows remain compatible with both views.
