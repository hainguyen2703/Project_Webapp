# Data Model: Remove Academia.edu — arXiv Only

**Feature**: `005-remove-academia-arxiv-only`  
**Date**: 2026-05-25

---

## Entities Changed

### `LATEST_RESULTS` (in-memory cache — `src/app.py`)

In-memory dict that caches the most recent fetch result per source for use by the detail view.

| | Before | After |
|---|---|---|
| Type | `dict[str, list[dict]]` | `dict[str, list[dict]]` |
| Keys | `"arxiv"`, `"academia"` | `"arxiv"` only |
| Initial value | `{"arxiv": [], "academia": []}` | `{"arxiv": []}` |
| Written by | `home()` — `LATEST_RESULTS[selected_source] = ...` | `home()` — `LATEST_RESULTS["arxiv"] = ...` (hardcoded) |
| Read by | `item_detail()` — `LATEST_RESULTS.get(source, [])` | `item_detail()` — `LATEST_RESULTS.get("arxiv", [])` (hardcoded) |

---

### `CONTENT_SOURCES` (runtime configuration — `src/app.py`)

List of active content source descriptors passed to the home template to render the source selector.

| | Before | After |
|---|---|---|
| Type | `list[dict]` with keys `id`, `name`, `description` | **REMOVED** |
| Value | `[{"id": "arxiv", ...}, {"id": "academia", ...}]` | N/A |
| Consumed by | `home()` — passed as `sources` in template context | No longer exists |
| Template use | `{% for src in sources %} <option> ...` in `home.html` | Selector block removed from template |

---

## Entities Unchanged

### `ContentSource` dataclass (`src/models/source.py`)

```python
@dataclass
class ContentSource:
    id: str
    name: str
    display_name: str
    type: str
    fetch_endpoint: str
    description: str
```

**Status**: Retained as-is. No longer instantiated at runtime (CONTENT_SOURCES list is removed), but kept for future extensibility. No code changes required.

---

### `PaperArticle` model (`src/models/article.py`)

**Status**: Unchanged. The `source` field on `PaperArticle` continues to hold the string `"arxiv"`. No schema changes.

---

### SQLite database (Flask-SQLAlchemy)

**Status**: Unchanged. Only user registration data is persisted. Source routing is entirely in-memory.

---

## State Transitions

### Route context after change

| Route | `source` value (before) | `source` value (after) |
|---|---|---|
| `GET /` (`home`) | from `request.args.get("source", "arxiv")` | hardcoded `"arxiv"` |
| `GET /api/listings` | from `request.args.get("source", "")` | hardcoded `"arxiv"` |
| `GET /detail/<id>` | from `request.args.get("source", "arxiv")` | hardcoded `"arxiv"` |

All three routes converge to the same `"arxiv"` value — no branching on source remains in any route.
