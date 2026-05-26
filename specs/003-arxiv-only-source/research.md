# Research: Simplify to arXiv-Only Source

**Feature**: 003-arxiv-only-source  
**Date**: 2026-05-26  
**Status**: Complete — all NEEDS CLARIFICATION resolved

---

## Decision 1: Home Button URL Strategy

**Question**: Should the "Home" button link to `url_for('home')` (no fetch) or `url_for('home', fetch=1)` (auto-fetch fresh results)?

**Decision**: Link to `url_for('home', fetch=1)` — always fetches fresh arXiv results.

**Rationale**: The spec requires that clicking "Home" while on the home page "reloads and displays a fresh set of results". Using `fetch=1` makes this consistent on every page: navigating home from any page always presents a current paper feed, not a blank page. This is the existing pattern used by the "Return to list" link in `detail.html`.

**Alternatives considered**:
- `url_for('home')` (no fetch): Lands on a blank home page with no results shown. Acceptable for pure navigation but inconsistent with the reload spec requirement.
- JavaScript-based reload: Overkill for a server-rendered Flask app; plain link is simpler and sufficient.

---

## Decision 2: Backward Compatibility for `?source=medium` URLs

**Question**: What should happen when `?source=medium` is passed to the home route after Medium is deleted?

**Decision**: Hardcode the active source to `"arxiv"` in the home route, ignoring the `source` query parameter entirely.

**Rationale**: The spec requires "graceful fallback" for Medium bookmarked URLs. Ignoring the `source` param and always serving arXiv is the simplest and safest implementation. The param will still be accepted by Flask (no 400 error) but will have no effect — arXiv results are served regardless.

**Implementation**:
- `app.py` home route: remove `selected_source = request.args.get("source", "arxiv")` and replace with `selected_source = "arxiv"` (or simply use `"arxiv"` literal throughout).
- `app.py` `/api/listings` route: keep `source` param validation — any value other than `"arxiv"` will naturally produce an "Unsupported source" error from `discovery_service.py` once the Medium branch is removed.

**Alternatives considered**:
- Redirect `?source=medium` to `?source=arxiv`: More correct RESTfully, but adds code complexity for a low-value edge case.
- Return HTTP 400 for `source=medium`: Too aggressive; existing user bookmarks should not receive errors.

---

## Decision 3: `CONTENT_SOURCES` List Disposal

**Question**: The `CONTENT_SOURCES` list in `app.py` is passed to `home.html` for the dropdown. After the dropdown is removed, is this list still needed?

**Decision**: Remove `CONTENT_SOURCES` entirely from `app.py` and stop passing it to the template context.

**Rationale**: The list serves no purpose without the dropdown. Leaving it in the code would be misleading dead code, violating Constitution Principle I (modularity, no dead code).

**Alternatives considered**:
- Keep as documentation of available sources: No value; the single valid source (`arxiv`) is evident from the code itself.

---

## Decision 4: `LATEST_RESULTS` Dictionary Scope

**Question**: `LATEST_RESULTS` in `app.py` is currently `{"arxiv": [], "medium": []}`. Should the `"medium"` key be removed?

**Decision**: Simplify to `{"arxiv": []}`.

**Rationale**: The `"medium"` key is purely dead storage after Medium is removed. Keeping it would be misleading and violates Constitution Principle I. The `item_detail` route uses `LATEST_RESULTS.get(source, [])` — with `source` hardcoded to `"arxiv"` in the home route, the `"medium"` key is never populated or accessed.

**Alternatives considered**:
- Leave `"medium"` key in place: No impact at runtime but is misleading dead code.

---

## Decision 5: Test Coverage for Removed Medium Code

**Question**: What test changes are required when `medium_client.py` is deleted and the Medium branch removed from `discovery_service.py`?

**Decision**: Remove `test_fetch_medium_articles` from `test_source_clients.py`. Remove `test_error_state_shows_retry` Medium fixture from `test_discovery_flow.py` and replace with an arXiv-specific error test. Add a test that verifies the "Home" button is present in rendered HTML.

**Rationale**: Tests must reflect the current system state. Keeping a test for deleted code will cause import errors (`from src.clients import medium_client`). Constitution Principle I requires tests that verify behavior, not legacy behavior of deleted code.

**Test additions**:
- `test_discovery_flow.py`: `test_home_button_visible` — verify `b'Home'` (or `b'href="/"`) appears in rendered home and detail templates.
- `test_discovery_flow.py`: `test_arxiv_error_shows_retry` — replace the Medium error test with an arXiv error scenario.
- `test_source_clients.py`: Remove Medium sample XML fixture and `test_fetch_medium_articles` function; remove `medium_client` import.
