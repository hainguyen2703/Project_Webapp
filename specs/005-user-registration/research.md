# Research: User Registration

**Feature**: 005-user-registration  
**Date**: 2026-06-02  
**Status**: Complete

## Decision 1: Persistence layer and schema strategy

**Decision**: Use SQLite (`sqlite3`) with a small schema bootstrap on app startup.

**Rationale**: SQLite is explicitly requested, requires no new infrastructure, and fits the current single-process Flask architecture. A unique constraint on normalized email enforces duplicate-account prevention at the database boundary in addition to application validation.

**Alternatives considered**:
- In-memory account store: rejected because accounts would be lost on restart and uniqueness could not be guaranteed across process restarts.
- External database (PostgreSQL/MySQL): rejected as unnecessary operational complexity for current scope.

## Decision 2: Password security implementation

**Decision**: Use Werkzeug security helpers (`generate_password_hash` and `check_password_hash`) with explicit hashing method configuration.

**Rationale**: Werkzeug is explicitly requested and already available with Flask. The helpers provide battle-tested salted password hashing and verification APIs, avoiding custom crypto code.

**Alternatives considered**:
- Plaintext or reversible encryption: rejected due to severe security risk.
- Custom hashing implementation: rejected to avoid cryptographic mistakes and maintenance risk.

## Decision 3: Validation and normalization rules

**Decision**: Enforce server-side validation for required fields, password policy (minimum 8 chars, at least one letter and one number), duplicate email checks, and explicit rejection of emails with leading/trailing whitespace.

**Rationale**: These rules are directly specified in FR-003, FR-004, FR-005, FR-006, and FR-012, and must be deterministic and testable from backend behavior even if client-side checks exist.

**Alternatives considered**:
- Trimming whitespace automatically: rejected because clarifications require whitespace to be invalid and rejected.
- Client-side-only validation: rejected because it is bypassable and does not protect integrity.

## Decision 4: Handling rapid duplicate submissions

**Decision**: Add a single-flight submission guard using a hidden form token and short-lived in-memory tracking keyed by session + token; process first valid submission and reject later in-flight duplicates.

**Rationale**: FR-011 requires processing only the first valid submission when rapid duplicate posts occur. A token-based guard is straightforward for server-rendered forms and complements DB uniqueness.

**Alternatives considered**:
- Rely only on unique-email constraint: rejected because duplicate submissions could still cause noisy error paths and non-deterministic UX.
- Full distributed idempotency infrastructure: rejected as out of scope for current single-node app.

## Decision 5: Signed-in user registration behavior

**Decision**: Keep `/register` accessible while signed in and allow creation of another account if submitted email is unique.

**Rationale**: This behavior is explicitly set by clarification and must be preserved in routing and UI logic.

**Alternatives considered**:
- Block signed-in registration or require sign-out: rejected because it conflicts with accepted clarification.
