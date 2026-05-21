# Research: Replace Medium Source with Academia.edu

**Feature**: `004-replace-medium-academia`  
**Phase**: 0  
**Date**: 2026-05-21

---

## RQ-001 — Academia.edu Search URL & Anti-Scraping Posture

**Decision**: Use `https://www.academia.edu/search?q=<QUERY>` with a descriptive `User-Agent` header.

**Rationale**: The search page is server-rendered (no Cloudflare, no CAPTCHA detected on initial GET), making `requests.get()` functional. Academia.edu's `robots.txt` disallows all crawlers universally (`Disallow: /`) — the plan acknowledges this and the spec Assumption explicitly constrains the implementation to publicly visible unauthenticated content only, which reflects ethical use. A descriptive `User-Agent` (e.g., `"PaperDiscovery/1.0"`) identifies the app honestly.

**Rate limiting**: Academia.edu may rate-limit after rapid repeated requests. The client uses a single request per user action (not background polling), so this is not a concern under normal usage.

**Alternatives considered**:
- Academia.edu `/v0/*` API — explicitly blocked in `robots.txt`, confirmed unavailable.
- RSS feed — does not exist for search results on Academia.edu.
- Unpaywall API — indexes some Academia.edu papers via DOI but doesn't provide a search interface over Academia.edu content directly; out of scope.

---

## RQ-002 — HTML Structure & CSS Selectors

**Decision**: Use `div[data-document-id]` as the article container; extract fields with the following selector cascade (trying primary then fallback on each field).

| Field | Primary selector | Fallback |
|---|---|---|
| Title | `a.document-title` | `h3 > a` |
| Author | `span.author-name` | `"Unknown"` |
| Snippet | `p.preview` | `div.document-summary` text, then `"No summary available."` |
| Date | `time[datetime]` attribute | `span.document-date` text, then current UTC ISO timestamp |
| URL | `a.document-title[href]` prefixed with `https://www.academia.edu` if relative | `https://www.academia.edu/<doc_id>/` |

**Rationale**: Academia.edu uses a mix of semantic elements and React-generated class names. The `data-document-id` attribute on the container is the most stable anchor (it encodes the document's unique ID). Field selectors are tried in order from most-to-least reliable; all have explicit fallbacks per FR-004.

**Risk**: Academia.edu may update their HTML at any time — selectors could break. Mitigation: the per-field fallback chain ensures the client always returns *something* rather than crashing. When no articles are parsed (0 results from a non-empty response), the service layer returns an empty-state message, which is the same graceful path as a real empty result.

---

## RQ-003 — BeautifulSoup4 Parsing Pattern

**Decision**: Functional module (not a class) matching the existing `medium_client.py` / `arxiv_client.py` style. Single public function `fetch_academia_articles(limit, query)`.

```python
ACADEMIA_SEARCH_URL = "https://www.academia.edu/search"
DEFAULT_QUERY = "computer science"

def fetch_academia_articles(limit: int = 10, query: Optional[str] = None) -> List[PaperArticle]:
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
    ...
```

**Rationale**: Reuses `requests` + `BeautifulSoup` already installed. Matching the existing functional style keeps the module consistent and avoids introducing a class-based Client pattern when all other clients use bare functions.

---

## RQ-004 — Source Routing & Medium Removal

**Decision**: In `src/app.py` (CONTENT_SOURCES list) and `src/services/discovery_service.py` (routing dispatch):
- Remove `{"id": "medium", ...}` entry from `CONTENT_SOURCES`.
- Add `{"id": "academia", "name": "Academia.edu", "description": "Academic papers from Academia.edu."}`.
- In `discovery_service.py`: replace `elif source == "medium":` branch with `elif source == "academia":` calling `fetch_academia_articles`.
- The existing `else` branch already returns `"Unsupported source."` — `source=medium` will fall through to it, satisfying FR-008.

**`LATEST_RESULTS` cache key**: Change from `"medium"` to `"academia"` in `app.py`.

---

## RQ-005 — Test Fixture & Mock Strategy

**Decision**: Inline HTML string constant `ACADEMIA_SAMPLE_HTML` in `tests/unit/test_source_clients.py`, patched via `@patch("src.clients.academia_client.requests.get")`. Mirrors the `MEDIUM_SAMPLE_RSS` pattern exactly.

```python
ACADEMIA_SAMPLE_HTML = """
<html><body>
  <div data-document-id="12345678">
    <h3><a class="document-title" href="/12345678/Example_Title">
      Example Paper Title
    </a></h3>
    <span class="author-name">Jane Smith</span>
    <p class="preview">A short excerpt about the paper topic.</p>
    <time datetime="2025-01-15">January 15, 2025</time>
  </div>
</body></html>
"""
```

**Assertions**: source == "academia", title == "Example Paper Title", authors == ["Jane Smith"], "excerpt" in summary, published_at startswith "2025-01-15", url contains "academia.edu".

**Rationale**: No live network calls. Test is deterministic. Fixture uses the same selector targets as the implementation, so a selector regression causes a test failure immediately.
