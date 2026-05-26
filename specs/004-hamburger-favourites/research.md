# Research: Hamburger Menu with Favourites

**Feature**: 004-hamburger-favourites  
**Date**: 2026-05-26  
**Status**: Complete — all NEEDS CLARIFICATION resolved

---

## Decision 1: Favourites Storage Strategy

**Question**: How should the favourites collection be stored? Options include Flask session (signed cookie), server-side in-memory dict, or an external session store.

**Decision**: Server-side in-memory dict (`FAVOURITES_STORE`) keyed by a per-user UUID stored in `session['user_id']`.

**Rationale**: Flask's built-in signed-cookie session is limited to ~4KB, which can hold at most 3–8 full paper records (each ~500–2000 bytes including the abstract). Storing favourites server-side in a global dict avoids this limit entirely, adds no new dependencies, and is consistent with the existing `LATEST_RESULTS` in-memory pattern already used by the application. A UUID (generated with `secrets.token_urlsafe(32)`) is stored in the session cookie to identify the user — the cookie itself stays tiny (~50 bytes).

```python
FAVOURITES_STORE: dict[str, list[dict]] = {}  # user_id → [paper_dict, ...]
```

**Known limitation**: Data is lost when the server restarts, matching the same behaviour as `LATEST_RESULTS`. This is acceptable for the local development / single-session scope of the application.

**Alternatives considered**:
- Flask signed-cookie session with full paper dicts: Too large — hits the ~4KB browser cookie limit at 3–8 papers.
- Flask-Session with filesystem backend: Avoids size limits and survives server restarts, but adds a `flask-session` dependency. Out of scope for this feature.
- SQLite/file-based database: Persistent across restarts, but adds significant complexity. Out of scope.

---

## Decision 2: Heart Toggle Interaction Model

**Question**: How should clicking the heart button update the server-side favourites? The app is server-rendered (no SPA framework). Options include a full-page form POST, AJAX, or JavaScript fetch.

**Decision**: HTML `<form method="post">` POSTing to `/favourite/toggle` with the `item_id` hidden, followed by a server-side redirect back to the detail page (POST-Redirect-GET pattern).

**Rationale**: The existing app has no JavaScript beyond what the browser provides natively. A plain form POST is consistent with this approach, prevents form resubmission on back/refresh, and requires zero new client-side code.

**Implementation**:
- Detail template: `<form method="post" action="/favourite/toggle"><input type="hidden" name="item_id" value="{{ item.id }}"><button>♡ / ♥</button></form>`
- Toggle route: looks up paper from `LATEST_RESULTS["arxiv"]` (if adding) or `FAVOURITES_STORE[user_id]` (if removing), then redirects to `url_for('item_detail', item_id=item_id)`.
- Heart state: determined by checking `item.id in {f['id'] for f in FAVOURITES_STORE.get(user_id, [])}`, passed as `is_favourite` to the template.

**Alternatives considered**:
- AJAX/fetch with JSON API: More responsive UX (no full page reload) but requires JavaScript and a JSON endpoint. Inconsistent with the rest of the app.
- GET request with a toggle link: Violates HTTP semantics (state-changing action via GET); prone to accidental triggers (link prefetching, browser history).

---

## Decision 3: Hamburger Menu Implementation

**Question**: Should the hamburger menu use a CSS-only toggle (checkbox trick) or minimal JavaScript?

**Decision**: CSS-only toggle using a hidden `<input type="checkbox" id="nav-toggle">` paired with a `<label for="nav-toggle">` containing the ☰ icon. The `<nav>` content is shown/hidden via the CSS `:checked` sibling selector.

**Rationale**: Zero JavaScript required. Works in all modern browsers. Consistent with the server-rendered, no-JS approach of the existing app. The menu is simple (one link: Favourites), so the CSS technique is entirely sufficient.

**CSS pattern**:
```css
#nav-toggle { display: none; }
.hamburger-nav { display: none; }
#nav-toggle:checked ~ .hamburger-nav { display: block; }
```

**Alternatives considered**:
- JavaScript event listener: More flexible (close on outside click, animations) but introduces JS dependency inconsistent with the current codebase.
- Always-visible navigation link: Simpler but does not satisfy FR-006/FR-007 which explicitly require a hamburger icon and revealed menu.

---

## Decision 4: Detail Route Fallback for Favourited Papers (FR-011)

**Question**: The `/detail/<item_id>` route currently only looks up papers from `LATEST_RESULTS["arxiv"]`. How should it fall back to favourites-stored data?

**Decision**: Extend the lookup in `item_detail` to check `FAVOURITES_STORE.get(user_id, [])` after `LATEST_RESULTS["arxiv"]` fails. The first match wins.

**Implementation**:
```python
item = next((i for i in LATEST_RESULTS["arxiv"] if i.get("id") == item_id), None)
if item is None:
    user_id = session.get("user_id", "")
    item = next((i for i in FAVOURITES_STORE.get(user_id, []) if i.get("id") == item_id), None)
if item is None:
    abort(404)
```

**Alternatives considered**:
- Always re-fetch from arXiv by ID: Reliable but adds latency and an external network dependency for every detail page load from Favourites.
- Store a separate `FAVOURITED_DETAILS` dict: Redundant with `FAVOURITES_STORE`.

---

## Decision 5: Flask Secret Key

**Question**: `session['user_id']` requires Flask to sign the cookie with a secret key. How should this be configured?

**Decision**: Set `app.secret_key = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-in-prod")` in `app.py`. Import `os` and `secrets` at the top.

**Rationale**: Follows OWASP best practice — never hardcode a secret in source code. The environment variable allows production deployments to inject a real secret without code changes. The fallback string is intentionally labelled "insecure" and "dev-only" to discourage production use.

**Security note**: The UUID user identifier (`secrets.token_urlsafe(32)`) is unpredictable and collision-resistant. The session cookie is HMAC-signed by Flask, so it cannot be forged by a client. Public arXiv paper data stored server-side is non-sensitive.
