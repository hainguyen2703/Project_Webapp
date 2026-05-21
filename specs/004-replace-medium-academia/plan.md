# Implementation Plan: Replace Medium Source with Academia.edu

**Branch**: `004-replace-medium-academia` | **Date**: 2026-05-21 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/004-replace-medium-academia/spec.md`

## Summary

Replace the "Medium" content source with "Academia.edu" across the entire application. The implementation adds a new `academia_client.py` that scrapes Academia.edu's public search page using `BeautifulSoup4` (already installed), removes `medium_client.py`, updates the source routing in `discovery_service.py`, updates the source list in `app.py`, and replaces the Medium client test with an Academia.edu fixture test. No new dependencies, no model changes, no template changes.

## Technical Context

**Language/Version**: Python 3.12.13  
**Primary Dependencies**: Flask≥2.0, `requests≥2.28`, `beautifulsoup4≥4.12` (all already installed)  
**Storage**: N/A — no model changes  
**Testing**: pytest≥8.0, `unittest.mock.patch`, inline HTML fixture string  
**Target Platform**: Flask server-rendered web app  
**Project Type**: Web application, single-package Python  
**Performance Goals**: Same as existing clients — single `requests.get(timeout=10)` per fetch  
**Constraints**: Must use only publicly visible unauthenticated content; descriptive `User-Agent` header required; no live network calls in tests  
**Scale/Scope**: 1 new file, 1 deleted file, 3 modified files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Evaluation | Status |
|---|---|---|
| I. Code Quality & Maintainability | New client mirrors `medium_client.py` structure exactly; BeautifulSoup4 parsing with per-field fallbacks; test uses inline HTML fixture matching existing `MEDIUM_SAMPLE_RSS` pattern; `medium_client.py` deleted (no dead code) | **PASS** |
| II. User Experience Consistency | Source label "Academia.edu" replaces "Medium" uniformly in `CONTENT_SOURCES`, discovery service, and rendered results; error/empty states use existing `format_fetch_result` paths — no new UX patterns | **PASS** |
| III. Performance Requirements | Single HTTP GET per fetch, same `timeout=10`; BeautifulSoup parse overhead negligible at ≤10 results | **PASS** |

Post-design re-evaluation: No violations. Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/004-replace-medium-academia/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output
├── spec.md              # Feature spec
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

> Note: No `data-model.md` (no model changes) or `contracts/` (no new API endpoints).

### Source Code

```text
src/
└── clients/
    ├── academia_client.py   # NEW: BeautifulSoup4 scraper for Academia.edu
    └── medium_client.py     # DELETED

src/
└── services/
    └── discovery_service.py # MODIFIED: replace medium → academia routing

src/
└── app.py                   # MODIFIED: CONTENT_SOURCES + LATEST_RESULTS key

tests/
└── unit/
    └── test_source_clients.py  # MODIFIED: replace Medium test with Academia fixture test
```

**Structure Decision**: Single-package Flask web application. Change is confined to the existing `clients/` layer and its callers. No new modules, no new layers, no template changes.

## Design Decisions (from research.md)

### Client implementation

```python
# src/clients/academia_client.py — key outline
ACADEMIA_SEARCH_URL = "https://www.academia.edu/search"
DEFAULT_QUERY = "computer science"

def fetch_academia_articles(limit=10, query=None):
    search_query = query or DEFAULT_QUERY
    response = requests.get(
        ACADEMIA_SEARCH_URL,
        params={"q": search_query},
        headers={"User-Agent": "PaperDiscovery/1.0"},
        timeout=10,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    containers = soup.find_all("div", attrs={"data-document-id": True})[:limit]
    # Per-field extraction with fallbacks per RQ-002
```

### Selector cascade (per RQ-002)

| Field | Primary | Fallback |
|---|---|---|
| Title | `a.document-title` text | `h3 > a` text |
| Author | `span.author-name` text | `"Unknown"` |
| Snippet | `p.preview` text | `div.document-summary` text → `"No summary available."` |
| Date | `time[datetime]` attr | `span.document-date` text → current UTC ISO |
| URL | `a.document-title[href]` | `https://www.academia.edu/<doc_id>/` |

### Test fixture (per RQ-005)

Inline `ACADEMIA_SAMPLE_HTML` string in `test_source_clients.py`, patched via `@patch("src.clients.academia_client.requests.get")`. Replaces `MEDIUM_SAMPLE_RSS` and `test_fetch_medium_articles`.
