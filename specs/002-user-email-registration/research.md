# Research: User Email Registration

**Feature**: 002-user-email-registration  
**Phase**: 0 — Technical Unknowns  
**Date**: 2026-05-14

## Unknown 1: Storage / ORM

**Decision**: Flask-SQLAlchemy (≥3.0) with SQLite for v1  
**Rationale**: Flask-SQLAlchemy is the de facto standard for Flask apps; provides ORM abstraction over SQLite with zero infrastructure (file-based). The two entities required (User, VerificationToken) are simple relational structures; ORM relationships and type-safe column definitions reduce error surface. SQLite is sufficient for v1 user volume and can be migrated to PostgreSQL later without application code changes.  
**Alternatives considered**:
- Plain `sqlite3` module: Requires manual schema migrations and raw SQL string composition; not worth the saved dependency.
- No database (JSON files): Violates concurrency and data-integrity requirements for concurrent web requests.
- Other ORMs (Peewee, Tortoise): Less ecosystem support for Flask; Flask-SQLAlchemy is the community standard.

**Action**: Add `Flask-SQLAlchemy>=3.0` to `requirements.txt`.

---

## Unknown 2: Email Sending

**Decision**: Flask-Mail (SMTP, provider-agnostic configuration via environment variables)  
**Rationale**: Provider-agnostic: switching SMTP credentials switches provider without code changes. Single lightweight dependency. Flask app-context integration. Transactional verification emails are simple fire-and-forget; no webhooks or delivery tracking required for v1 (spec assumption: best-effort delivery).  
**Alternatives considered**:
- Raw `smtplib`: Manual connection management and configuration boilerplate; Flask-Mail abstracts this cleanly.
- External SDK (SendGrid, Mailgun, AWS SES): Adds costs, credential dependencies, and provider lock-in; unnecessary for v1.
- Async dispatch with Celery: Overkill for v1 — synchronous sending acceptable for registration flow.

**Action**: Add `Flask-Mail>=0.9.1` to `requirements.txt`. Configure `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_USE_TLS` via environment variables.

---

## Unknown 3: Password Hashing

**Decision**: `werkzeug.security.generate_password_hash()` / `check_password_hash()`  
**Rationale**: Werkzeug is bundled with Flask — zero additional dependencies. Uses PBKDF2-HMAC-SHA256 with random salt; cryptographically sound and production-grade. Satisfies FR-015 without added complexity.  
**Alternatives considered**:
- passlib + bcrypt: More flexible but adds 2 dependencies; unnecessary for v1.
- argon2-cffi: Superior GPU-resistance but adds binary compilation complexity; consider upgrading later if threat model grows.

**Action**: No new dependency. Use `werkzeug.security` directly.

---

## Unknown 4: Verification Token Generation

**Decision**: `secrets.token_urlsafe(32)` (Python stdlib)  
**Rationale**: 256-bit entropy; cryptographically secure via `os.urandom()`; URL-safe Base64 encoding; zero dependencies. Token is a single-use lookup key stored in the database alongside expiry and resend_count — no JWT parsing overhead needed. Stored indexed in `VerificationToken.token_value`.  
**Alternatives considered**:
- `uuid4()`: 128-bit entropy, not designed for security-sensitive tokens.
- JWT: Adds claim-parsing complexity; database storage of expiry makes JWT unnecessary.

**Action**: No new dependency. Use `secrets.token_urlsafe(32)` in service layer.

---

## Unknown 5: Post-Registration Session State ("Check Your Email" Page)

**Decision**: Flask signed session (cookie) for UX state; database as source of truth for security checks  
**Rationale**: Flask session is signed with `SECRET_KEY`; tamper-evident and built-in. Stores `registration_id`, `masked_email`, and `next_resend_allowed_at` for UX display. On resend form POST, database is authoritative (validates resend_count and cooldown). Email address in URL parameters avoided — it would appear in browser history, server logs, and HTTP referrer headers.  
**Alternatives considered**:
- URL parameters only: Privacy leak (email in URL) and tamper risk (resend_count spoofing).
- Pure database lookup with no Flask session: Requires separate session ID cookie; more complex than Flask's built-in session.

**Action**: Set `app.config['SECRET_KEY']` from environment variable. Populate session after successful registration; validate against DB on resend.

---

## Unknown 6: Pending Account Purge (FR-011 — 24-hour cleanup)

**Decision**: Lazy deletion triggered on registration and verification attempts  
**Rationale**: On every `POST /register` and `GET /verify/<token>`, execute a background cleanup query deleting `WHERE status='pending' AND created_at < NOW() - 24h`. No background worker infrastructure needed for v1. Stale accounts that never trigger a new registration are low-value to purge eagerly; lazy deletion is sufficient. Ensures email address is freed before the next registration attempt by the rightful owner.  
**Alternatives considered**:
- APScheduler (nightly cron): Cleaner for proactive cleanup but adds infrastructure; revisit in v1.5 if monitoring shows stale accumulation.
- Celery task queue: Overkill for v1 volume.

**Action**: Add `_purge_expired_pending_accounts()` utility called at start of register and verify handlers.
