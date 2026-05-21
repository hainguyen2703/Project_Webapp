# Feature Specification: Replace Medium Source with Academia.edu

**Feature Branch**: `004-replace-medium-academia`  
**Created**: 2026-05-21  
**Status**: Draft  
**Input**: User description: "Replace medium site by academia.edu"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Discover academic papers from Academia.edu (Priority: P1)

A user opens the paper discovery site, selects "Academia.edu" as the source, and receives a list of academic papers or articles fetched from Academia.edu. The "Medium" option is no longer present in the source selector.

**Why this priority**: This is the core requirement — replacing one source with another. Without this, the feature delivers no value. All other changes (labels, error messages, tests) depend on this being working first.

**Independent Test**: Select "Academia.edu" from the source dropdown and click "Fetch Listings". Confirm results appear with source label "Academia.edu". Confirm "Medium" is absent from the dropdown.

**Acceptance Scenarios**:

1. **Given** a user opens the home page, **When** they look at the source selector, **Then** "Academia.edu" is listed as a source option and "Medium" is not.
2. **Given** a user selects "Academia.edu" and clicks "Fetch Listings", **When** the request completes successfully, **Then** a list of articles is shown labelled with "Academia.edu" as the source.
3. **Given** a user selects "Academia.edu" and clicks "Fetch Listings", **When** Academia.edu is unreachable or returns no results, **Then** a user-friendly error or empty-state message is shown — no crash or stack trace.

---

### User Story 2 — View detail of an Academia.edu article (Priority: P2)

A user clicks "View details" on an Academia.edu result and is taken to the detail page, which shows the article's title, authors, summary, and a link back to the original Academia.edu page.

**Why this priority**: The detail view is part of the existing end-to-end flow. Without verifying it works with the new source, the feature is incomplete. It depends on US1 (articles must load before detail can be viewed).

**Independent Test**: Fetch Academia.edu results, click "View details" on any result. Confirm the detail page loads with correct article data and a working source link to Academia.edu.

**Acceptance Scenarios**:

1. **Given** Academia.edu results are shown, **When** a user clicks "View details" on an article, **Then** the detail page loads and shows the article's title, authors, summary, and a link to the original Academia.edu URL.
2. **Given** a user is on the detail page of an Academia.edu article, **When** they click the source link, **Then** they are navigated to the correct Academia.edu page in a new tab.

---

### Edge Cases

- What happens if Academia.edu requires authentication or blocks automated requests? The client must handle HTTP 4xx/5xx responses gracefully and show the error-state message rather than crashing.
- What happens if Academia.edu articles lack author information? The system must display a safe fallback (e.g., "Unknown") rather than an empty or broken field.
- What happens if Academia.edu articles have no publication date? The system must substitute a sensible default rather than displaying a blank or invalid date.
- What happens if a user navigates directly to a Medium detail URL (`/detail/...?source=medium`) after this change? The system must return an appropriate error (e.g., "Unsupported source") rather than crashing.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The source selector on the home page MUST include "Academia.edu" as a selectable source.
- **FR-002**: The source selector on the home page MUST NOT include "Medium" as a selectable source.
- **FR-003**: Selecting "Academia.edu" and fetching MUST return a list of articles retrieved from Academia.edu.
- **FR-004**: Each article result retrieved from Academia.edu MUST display: title, authors (or "Unknown" fallback), summary sourced from the excerpt/snippet text visible on the search results page (or "No summary available" if absent), the Academia.edu upload/posting date visible on the search results page (or current date as fallback if absent), and source label "Academia.edu".
- **FR-005**: The detail view MUST work for Academia.edu articles, displaying the same fields as FR-004 plus a link to the original Academia.edu article URL.
- **FR-006**: If Academia.edu is unavailable or returns an error, the application MUST display a user-friendly error message and MUST NOT expose a stack trace or crash.
- **FR-007**: All references to "Medium" in user-visible text (labels, headings, descriptions) MUST be replaced with "Academia.edu" or removed entirely.
- **FR-008**: The `medium` source identifier MUST be removed from the internal source routing; requests with `source=medium` MUST return an "Unsupported source" error response.
- **FR-009**: When no search keyword is provided by the user, the Academia.edu client MUST use "computer science" as the default query term.
- **FR-010**: The automated test suite MUST test the Academia.edu client using a saved HTML fixture (mocked HTTP response); no live network calls to Academia.edu are permitted in tests.

### Key Entities

- **ContentSource**: The data structure representing an available discovery source. The `medium` entry is removed and an `academia` entry is added.
- **AcademiaArticle**: An article fetched from Academia.edu, mapped to the existing `PaperArticle` model fields used by the rest of the application.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: "Medium" does not appear anywhere in the source selector on the home page.
- **SC-002**: A fetch from "Academia.edu" returns at least 1 result under normal network conditions.
- **SC-003**: All automated tests pass (no regression on arXiv flow, registration flow, or navigation).
- **SC-004**: A request with `source=medium` returns a non-200 error response or a structured error payload — no unhandled exception.

## Assumptions

- Academia.edu's public search results page (`/search`) is accessible without authentication and will be used as the data source via HTML parsing (scraping). No API key is required.
- The existing `PaperArticle` model fields (title, authors, summary, url, published_at, source_label) are sufficient to represent Academia.edu articles without model changes.
- The arXiv source is unaffected by this change.
- The registration flow (feature 002) and navigation dropdown (feature 003) are unaffected by this change.
- No URL migration or redirect is required for previously bookmarked Medium detail URLs; returning an "Unsupported source" error is acceptable.
- The application must not circumvent any authentication wall; only publicly visible (unauthenticated) page content may be parsed.
- The article summary field is populated from the short excerpt/snippet shown on the Academia.edu search results page; fetching full abstracts from individual article pages is out of scope.
- The publication date field uses the Academia.edu upload/posting date shown on the search results page; the paper's original publication year is not used.
- The Academia.edu client test uses a saved HTML fixture to mock HTTP responses, consistent with the existing Medium and arXiv client test pattern.

## Clarifications

### Session 2026-05-21

- Q: How should the application retrieve articles from Academia.edu? → A: HTML scraping — parse Academia.edu's public search results page (no API key needed).
- Q: What should the client fetch when no search keyword is provided? → A: Default topic "computer science".
- Q: What should be shown as the article summary? → A: Search page snippet — the short excerpt/preview text visible on the Academia.edu search results page.
- Q: What date should be shown as the publication date? → A: Academia.edu upload date — the date the paper was posted/uploaded to the platform, as shown on search results.

### Session 2026-05-21 (continued)

- Q: How should the Academia.edu client be tested in the automated test suite? → A: Mock with HTML fixture — tests use a saved sample HTML response; no live network calls.
