# Research: User-Owned Favourites

**Feature**: 008-user-owned-favourites  
**Date**: 2026-06-07  
**Status**: Complete

## Decision 1: Persistence model for favourites ownership

**Decision**: Store favourites in SQLite with explicit `user_id` ownership rather than in process memory.

**Rationale**: The spec requires favourites to remain available to the same authenticated user across sessions and to stay isolated between users. Process memory keyed by ad-hoc session tokens cannot satisfy durable ownership guarantees.

**Alternatives considered**:
- Keep in-memory `FAVOURITES_STORE` keyed by session token: rejected because data is lost on restart and ownership is not tied to real user accounts.
- Client-side browser storage only: rejected because it cannot provide server-enforced user isolation and account-lifecycle cleanup.

## Decision 2: Uniqueness key enforcement

**Decision**: Enforce favourite uniqueness per user using `(user_id, source, external_paper_id)`.

**Rationale**: Clarification established paper identity as `(source, external_paper_id)`. Combining with `user_id` ensures one favourite per paper per user while allowing different users to save the same paper independently.

**Alternatives considered**:
- URL-only uniqueness: rejected because URLs can vary while referring to the same paper.
- Title/author heuristic matching: rejected because it is not stable and can collide.

## Decision 3: Route access behavior for unauthenticated users

**Decision**: Hide favourites navigation when logged out and return generic 404 for unauthenticated direct access to favourites routes.

**Rationale**: This directly matches the clarified requirement and avoids exposing user-specific surface area while maintaining predictable behavior.

**Alternatives considered**:
- Redirect to login with return URL: rejected because clarification selected hidden navigation + not-found behavior.
- Return 401/403 responses: rejected because this leaks route existence more than the selected approach.

## Decision 4: Favourites ordering and mutation semantics

**Decision**: Persist created timestamp and always list favourites in descending `created_at` order; toggle/remove operations must preserve this ordering model.

**Rationale**: Clarification requires most-recent-first display. Database-level timestamp ordering is deterministic and aligns with UX expectations.

**Alternatives considered**:
- Alphabetical ordering: rejected by clarification.
- Insertion-order list in memory: rejected because it is non-durable and less explicit than timestamp sorting.

## Decision 5: Account deletion lifecycle

**Decision**: Cascade-delete all favourites immediately when a user account is deleted.

**Rationale**: Clarification explicitly mandates immediate deletion. This minimizes residual data risk and simplifies privacy/compliance reasoning.

**Alternatives considered**:
- Delayed purge/soft-delete: rejected by clarification.
- Anonymous retained metadata: rejected by clarification and outside feature scope.

## Decision 6: Performance guardrails and indexing

**Decision**: Add DB indexes/constraints for ownership and listing paths, including unique index on `(user_id, source, external_paper_id)` and retrieval index on `(user_id, created_at DESC)`.

**Rationale**: Constitution requires explicit performance targets. Indexed reads and writes keep add/remove/list operations within target latency bounds as favourites volume grows.

**Alternatives considered**:
- No additional indexes: rejected due to avoidable full scans and unpredictable latency.
- Over-normalized multi-table schema: rejected as unnecessary complexity for current scope.

## Residual Risks

- Legacy in-memory favourites may be lost during migration to account-owned persistence unless an explicit migration path is added later.
- If paper payload shape evolves, persisted snapshot compatibility must be validated in tests.
- Current feature scope assumes account deletion is represented in service layer, but endpoint wiring may be introduced in a later feature.
