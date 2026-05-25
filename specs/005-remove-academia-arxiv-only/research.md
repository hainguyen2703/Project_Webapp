# Research: Remove Academia.edu — arXiv Only

**Feature**: `005-remove-academia-arxiv-only`  
**Date**: 2026-05-25  
**Source**: Live codebase inspection (`src/`, `tests/`, `specs/`)

---

## 1. All Academia.edu References in the Codebase

**Decision**: The following are the complete set of locations that must be changed or deleted.

| File | Change | Detail |
|---|---|---|
| `src/clients/academia_client.py` | DELETE | Entire file; 90-line HTML scraper |
| `src/services/discovery_service.py` | MODIFY | Remove `from src.clients.academia_client import fetch_academia_articles`; remove `elif source == "academia":` branch |
| `src/app.py` | MODIFY | See §3 below for full route-by-route breakdown |
| `src/templates/home.html` | MODIFY | Remove `<select id="source">` block and `<label for="source">`; fix heading and URLs (see §4) |
| `src/templates/detail.html` | MODIFY | Remove `source=source` from the "Return to list" `url_for` call |
| `tests/unit/test_source_clients.py` | MODIFY | Remove `academia_client` import, `ACADEMIA_SAMPLE_HTML` constant, `test_fetch_academia_articles` function |
| `tests/integration/test_discovery_flow.py` | MODIFY | Update assertions and request URLs (see §5) |

**Rationale**: Confirmed by `grep` over `tests/` and `src/`. No other files contain `academia` references.

**Alternatives considered**: Keeping `academia_client.py` as an unused file — rejected; dead code violates Principle I (Code Quality).

---

## 2. Route Architecture After Change

**Decision**: All three routes become source-agnostic by hardcoding `"arxiv"` internally.

| Route | Before | After |
|---|---|---|
| `GET /` | reads `source` from query string, passes `CONTENT_SOURCES` to template | hardcodes `source = "arxiv"`, removes `sources` from context |
| `GET /api/listings` | reads `source` param, returns 400 if missing | hardcodes `source = "arxiv"`, ignores any `source` param |
| `GET /detail/<id>` | reads `source` param to select cache key | hardcodes `source = "arxiv"`, always looks up `LATEST_RESULTS["arxiv"]` |

**Rationale**: Minimal change surface — routes keep their structure but stop branching on source. Silently ignoring unknown query params is the standard Flask/HTTP behaviour; no special rejection needed.

**Alternatives considered**: Refactoring routes to remove `source` concept entirely from function signatures — deferred; not required for a correct delivery and would increase diff size with no user-facing benefit.

---

## 3. `src/app.py` Change Breakdown

**Decision**: Surgical edits to each route; configuration variables cleaned up.

### Variable changes
```python
# REMOVE entirely:
CONTENT_SOURCES = [...]

# CHANGE from:
LATEST_RESULTS: dict[str, list[dict]] = {"arxiv": [], "academia": []}
# CHANGE to:
LATEST_RESULTS: dict[str, list[dict]] = {"arxiv": []}
```

### `home()` route
```python
# REMOVE:
selected_source = request.args.get("source", "arxiv")
# ADD:
selected_source = "arxiv"

# REMOVE from context dict:
"sources": CONTENT_SOURCES,

# Cache write lines (both success and error paths) remain correct as-is
# since selected_source is now always "arxiv"
```

### `api_listings()` route
```python
# REPLACE entire function body to:
source = "arxiv"
query = request.args.get("query")
result = fetch_items(source, query=query)
if result["status"] == "error":
    return jsonify(result), 503
return jsonify(result)
```

### `item_detail()` route
```python
# REMOVE:
source = request.args.get("source", "arxiv")
# ADD:
source = "arxiv"
# Everything else unchanged — LATEST_RESULTS.get("arxiv", []) works correctly
```

---

## 4. Template Change Breakdown

**Decision**: Remove selector; fix hardcoded source label; clean up URL params.

### `src/templates/home.html`
```html
<!-- REMOVE this block: -->
<label for="source">Source</label>
<select id="source" name="source">
  {% for src in sources %}
    <option value="{{ src.id }}" {% if src.id == selected_source %}selected{% endif %}>{{ src.name }}</option>
  {% endfor %}
</select>

<!-- The form POST target and query input remain unchanged -->

<!-- CHANGE heading from: -->
<h2>Results from {{ selected_source | capitalize }}</h2>
<!-- CHANGE heading to: -->
<h2>Results from arXiv</h2>

<!-- CHANGE detail link from: -->
<a ... href="{{ url_for('item_detail', item_id=item.id, source=selected_source) }}">View details</a>
<!-- CHANGE detail link to: -->
<a ... href="{{ url_for('item_detail', item_id=item.id) }}">View details</a>

<!-- CHANGE retry link from: -->
<a href="{{ url_for('home', source=selected_source, query=query, fetch=1) }}">Retry</a>
<!-- CHANGE retry link to: -->
<a href="{{ url_for('home', query=query, fetch=1) }}">Retry</a>
```

### `src/templates/detail.html`
```html
<!-- CHANGE return link from: -->
<a href="{{ url_for('home', source=source, fetch=1) }}">Return to list</a>
<!-- CHANGE return link to: -->
<a href="{{ url_for('home', fetch=1) }}">Return to list</a>
```

---

## 5. Test Update Strategy

**Decision**: Update only the assertions and requests that break due to the source-parameter and heading changes; leave all other test logic intact.

### `tests/unit/test_source_clients.py`
Remove:
- Line 3: `from src.clients import arxiv_client, academia_client` → `from src.clients import arxiv_client`
- Lines 18–45: `ACADEMIA_SAMPLE_HTML` constant
- Lines 47–58: `test_fetch_academia_articles` function

Net: 1 test removed (48 → 47 tests).

### `tests/integration/test_discovery_flow.py`

**`test_homepage_displays_results`**:
- `client.get("/?source=arxiv&fetch=1")` → `client.get("/?fetch=1")` (source param removed from URL)
- `assert b"Results from Arxiv"` → `assert b"Results from arXiv"` (heading now hardcoded)

**`test_detail_view_shows_source_link`**:
- `client.get("/?source=arxiv&fetch=1")` → `client.get("/?fetch=1")`
- `client.get("/detail/...?source=arxiv")` → `client.get("/detail/...")`

**`test_error_state_shows_retry`**:
- `client.get("/?source=medium&fetch=1")` → `client.get("/?fetch=1")`
- Mock still injects error result; `assert b"Medium is unavailable."` and `assert b"Retry"` still pass

**Rationale**: `test_models.py` uses `source="medium"` in a `PaperArticle` fixture — this is testing model validation, not the live source routing, so it is unaffected and must not be changed.

---

## 6. CONTENT_SOURCES / Template Variable Impact

**Decision**: Remove `sources` from the template context entirely; the `home.html` template no longer iterates over it.

After removing the `<select>` loop from `home.html`, the template no longer references `sources`, `selected_source` (except in the hardcoded heading), or `source=selected_source` URL params. The `context` dict in `home()` changes from:

```python
context = {"sources": CONTENT_SOURCES, "selected_source": selected_source, "query": query}
```

to:

```python
context = {"query": query}
```

`selected_source` is still used internally in the route (for `LATEST_RESULTS["arxiv"]`) but no longer needs to be in the template context since no template variable references it after the heading is hardcoded.

**Rationale**: Passing unused variables to templates is dead code (violates Principle I).
