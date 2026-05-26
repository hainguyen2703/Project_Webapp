# Data Model: Simplify to arXiv-Only Source

**Feature**: 003-arxiv-only-source  
**Date**: 2026-05-26

---

## Entities

### PaperArticle *(unchanged)*

The core data entity. No structural changes required. The `source` field will only ever hold `"arxiv"` after this feature, but its type and validation rules are unchanged.

| Field | Type | Constraints | Change |
|-------|------|-------------|--------|
| `id` | `str` | Non-empty; valid URL | None |
| `source` | `str` | Non-empty; was `"arxiv"` or `"medium"`; now always `"arxiv"` | Value constrained to `"arxiv"` only |
| `title` | `str` | Non-empty | None |
| `authors` | `list[str]` | Non-empty list | None |
| `summary` | `str` | Non-empty | None |
| `url` | `str` | Valid URL with scheme and netloc | None |
| `published_at` | `str` | ISO 8601 datetime string | None |
| `source_label` | `str` | Display label; always `"arXiv"` | Value constrained to `"arXiv"` only |
| `fetched_at` | `str` | ISO 8601 datetime string | None |
| `thumbnail_url` | `Optional[str]` | Valid URL or None | None |
| `metadata` | `dict[str, str]` | Arbitrary key-value pairs | None |

**File**: `src/models/article.py` — **no changes needed**

---

### ContentSource *(removed from active use)*

The `ContentSource` dataclass in `src/models/source.py` is not currently instantiated anywhere in the application (the `CONTENT_SOURCES` list in `app.py` uses plain dicts). It is left in place as it is out of scope for this feature, but it is effectively unused.

---

## Application State

### LATEST_RESULTS *(simplified)*

In-memory store in `src/app.py`.

**Before**:
```python
LATEST_RESULTS: dict[str, list[dict]] = {"arxiv": [], "medium": []}
```

**After**:
```python
LATEST_RESULTS: dict[str, list[dict]] = {"arxiv": []}
```

**Reason**: `"medium"` key is dead storage once Medium is deleted. Removing it eliminates misleading state.

---

## Removed Entities

### CONTENT_SOURCES list *(deleted)*

Previously defined in `src/app.py` to populate the source dropdown in `home.html`:

```python
CONTENT_SOURCES = [
    {"id": "arxiv", "name": "arXiv", "description": "Recent academic papers from arXiv."},
    {"id": "medium", "name": "Medium", "description": "Recent articles from Medium."},
]
```

After the dropdown is removed, this list serves no purpose and is deleted.

---

## Validation Rules (unchanged)

`PaperArticle.validate()` enforces:
- `id`, `source`, and `title` must be non-empty strings
- `url` must have a valid scheme and netloc (parsed via `urllib.parse.urlparse`)
- `published_at` must be a parseable ISO 8601 datetime string

No changes to these rules are required.

---

## State Transitions

The arXiv fetch flow is unchanged:

```
Home page loaded
    └─► User clicks "Fetch Listings" (or Home button with fetch=1)
            └─► GET /?fetch=1
                    └─► fetch_items("arxiv", query)
                            └─► fetch_arxiv_articles(limit, query)
                                    └─► arXiv API → list[PaperArticle]
                                            └─► LATEST_RESULTS["arxiv"] updated
                                                    └─► home.html rendered with results
```
