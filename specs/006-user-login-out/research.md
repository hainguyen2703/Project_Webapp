# Research: User Login and Logout

**Feature**: 006-user-login-out  
**Date**: 2026-06-03  
**Status**: Complete

## Decision 1: Authentication framework

**Decision**: Use Flask-LoginManager for session lifecycle and authenticated-user tracking.

**Rationale**: This was explicitly requested and fits the current Flask architecture. It provides battle-tested login session management, `current_user` integration in templates/routes, and clear hooks for login-required behavior.

**Alternatives considered**:
- Custom session management only with raw `session` dict: rejected due to higher maintenance and security risk.
- JWT/stateless auth: rejected as unnecessary complexity for this server-rendered app.

## Decision 2: Credential verification source

**Decision**: Authenticate against existing SQLite user accounts created by registration flow, using stored Werkzeug password hashes.

**Rationale**: Reuses existing data model and security primitives; no duplicate user store.

**Alternatives considered**:
- Separate auth table: rejected because it duplicates account identity and increases synchronization risk.
- External identity provider: rejected as out of scope.

## Decision 3: Throttling repeated failed login attempts

**Decision**: Apply temporary in-memory throttle keyed by identity and session context after repeated rapid failed attempts.

**Rationale**: Matches clarified requirement and offers practical protection against brute-force bursts without infrastructure changes.

**Alternatives considered**:
- No throttling: rejected due to security exposure.
- Immediate account lock on first rapid retry: rejected as too aggressive for user experience.

## Decision 4: Signed-out logout behavior

**Decision**: Block logout requests from signed-out users with 401/403 response semantics and no state changes.

**Rationale**: Explicit clarification mandates this behavior.

**Alternatives considered**:
- Idempotent success for signed-out logout: rejected due to clarification conflict.

## Decision 5: Session expiration handling

**Decision**: Auto-refresh expired user sessions on next protected action without forcing re-authentication.

**Rationale**: Required by accepted clarification despite increased security sensitivity. Implementation should document this tradeoff and constrain refresh scope.

**Alternatives considered**:
- Redirect to login on expiration: rejected due to clarification conflict.
- Silent action failure: rejected due to poor UX and unclear state.

## Decision 6: Logout invalidation scope

**Decision**: Invalidate all active sessions for the user across devices when logout occurs.

**Rationale**: Required by accepted clarification; improves security for account termination events.

**Alternatives considered**:
- Invalidate only current session: rejected due to clarification conflict.
