# Feature Specification: Remove Academia.edu — arXiv Only

**Feature Branch**: `005-remove-academia-arxiv-only`  
**Created**: 2026-05-25  
**Status**: Draft  
**Input**: User description: "Xóa kết nối với academia, chỉ giữ lại arxiv"

## Clarifications

### Session 2026-05-25

- Q: Should the source selector/dropdown be removed entirely or retained with a single "arXiv" option? → A: Remove entirely — arXiv is the implicit, hardcoded source.
- Q: Should the `/api/listings` `source` query parameter be retained (defaulting to arXiv) or removed entirely? → A: Remove entirely — the endpoint always fetches from arXiv with no parameter required or accepted.
- Q: Should the `CONTENT_SOURCES` list in `app.py` and the `ContentSource` dataclass in `source.py` be removed along with the source selector? → A: Remove `CONTENT_SOURCES` list only; retain the `ContentSource` dataclass in `source.py` for future extensibility.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Academia.edu Removed, arXiv Fetch Works (Priority: P1)

A visitor to the home page sees the search form without any source selector. They enter a keyword (or leave it blank) and click "Fetch Listings". arXiv results are returned as normal. No source dropdown is present and no reference to Academia.edu appears anywhere on the page.

**Why this priority**: This is the core change requested — removing the Academia.edu integration and the now-redundant source selector, while keeping arXiv fully functional. It is the minimum deliverable that satisfies the feature.

**Independent Test**: Open `GET /` and confirm no source selector element exists in the rendered HTML. Confirm no `value="academia"` or `value="arxiv"` selector is present. Fetch arXiv results and confirm they return successfully.

**Acceptance Scenarios**:

1. **Given** the application home page is open, **When** the page renders, **Then** no source dropdown is present and no reference to "Academia.edu" appears.
2. **Given** the user leaves the search field blank and clicks Fetch Listings, **When** the request completes, **Then** arXiv results are returned with title, authors, date, and summary.
3. **Given** a user navigates directly to `GET /api/listings?source=academia`, **When** the request is processed, **Then** arXiv results are returned — the unrecognised parameter is silently ignored.

---

### User Story 2 — arXiv Detail View Remains Functional (Priority: P2)

After fetching arXiv results, a visitor clicks "View details" on any result and sees the full detail page — title, authors, summary, and a link to the original arXiv URL. The detail view is unaffected by the removal of Academia.edu.

**Why this priority**: Regression protection — the detail view must remain intact after source cleanup.

**Independent Test**: Fetch arXiv results, then `GET /detail/<id>` and confirm a 200 response with all article fields and a link containing `arxiv.org`.

**Acceptance Scenarios**:

1. **Given** arXiv results have been fetched, **When** the user clicks "View details" on a result, **Then** the detail page loads with title, authors, summary, and a working link to the original arXiv paper.
2. **Given** the detail page is open for an arXiv article, **When** the user inspects the source link, **Then** it points to `arxiv.org`.

---

### Edge Cases

- What happens when `source=academia` is passed directly via the API URL? → The `source` parameter is no longer accepted; its presence is silently ignored and arXiv results are returned.
- What happens if the only remaining source (arXiv) is unavailable (network error)? → A user-friendly error message is shown; no stack trace is exposed.
- What happens to any cached Academia.edu results from a previous session? → Stale cache entries for `academia` are removed; only the `arxiv` cache key is retained.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The source selector dropdown MUST be absent from the home page rendered HTML entirely; arXiv is the sole implicit content source requiring no user selection, and no reference to "Academia.edu" MUST appear.
- **FR-002**: All Academia.edu client code, imports, and references MUST be removed from the application.
- **FR-003**: The `/api/listings` endpoint MUST NOT accept a `source` parameter; the endpoint always fetches from arXiv regardless of any query parameters passed.
- **FR-004**: arXiv fetching, search, and display MUST continue to work identically to before this change.
- **FR-005**: The detail view route MUST continue to work correctly for arXiv articles.
- **FR-006**: All existing automated tests for arXiv and all other unrelated features (registration, navigation) MUST continue to pass.
- **FR-007**: The Academia.edu unit test MUST be removed; the arXiv unit test MUST remain and pass.
- **FR-009**: The `CONTENT_SOURCES` configuration list MUST be removed from the application; the `ContentSource` dataclass MUST be retained as-is without modification.

### Key Entities

- **ContentSource dataclass**: The data model representing a content source (id, name, description, etc.). Retained unchanged for future extensibility — no longer instantiated at runtime.
- **CONTENT_SOURCES list**: The runtime configuration list of active sources passed to the UI. Removed entirely as part of this feature.
- **LATEST_RESULTS cache**: In-memory store keyed by source ID. After this change, simplified to hold only the arXiv result set.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The home page rendered HTML contains no source selector/dropdown element. No reference to "Academia.edu" appears in the rendered HTML. arXiv is the sole implicit source.
- **SC-002**: `GET /api/listings` (no parameters) returns a successful response with at least one arXiv result under normal network conditions.
- **SC-003**: `GET /api/listings?source=academia` returns the same arXiv results as `GET /api/listings` — the unrecognised parameter is silently ignored.
- **SC-004**: All automated tests pass with no new failures introduced; the Academia.edu-specific test is absent from the suite.
- **SC-005**: arXiv detail view loads correctly and the source link resolves to `arxiv.org`.

## Assumptions

- The application currently has exactly two sources: arXiv and Academia.edu. Only Academia.edu is being removed.
- No other parts of the codebase (templates, routes, models) reference Academia.edu in ways that would require changes beyond the client, service, and app configuration.
- The `ContentSource` dataclass in `source.py` requires no changes and is retained as-is. Only the `CONTENT_SOURCES` list in `app.py` (which instantiated the sources) is removed.
- No persistent database stores the list of sources; the source list is defined in application configuration.
- The `tests/unit/test_source_clients.py` file contains the Academia.edu test that must be removed.
- arXiv, user registration, and navigation dropdown features are entirely out of scope and must not be modified.
