# Feature Specification: Hamburger Menu with Favourites

**Feature Branch**: `004-hamburger-favourites`  
**Created**: 2026-05-26  
**Status**: Draft  
**Input**: User description: "Add a hamburger option which include: 'favourite' which is used to store favourite papers. A favourite button (present as a heart) in detail paper, if user click on this heart button, the current paper will be stored and can be read again in 'favourite' option of Hamburger."

## Clarifications

### Session 2026-05-26

- Q: Can users remove a paper from favourites directly from the Favourites page? → A: Yes — add a remove control (× button) on each item on the Favourites page
- Q: In what order are saved papers displayed on the Favourites page? → A: Most recently added first — newest saved paper appears at the top

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Save a Paper to Favourites (Priority: P1)

A user is reading a paper on the detail page and wants to save it for later. They click the heart button displayed on the page. The heart fills to indicate the paper is saved. If they click the heart again, the paper is removed from their favourites and the heart returns to its unfilled state.

**Why this priority**: Saving a paper is the core action the feature is built around. Without this, the Favourites list has no content. It is independently valuable — users can save papers even before the Favourites page is built.

**Independent Test**: Can be fully tested by visiting a paper detail page, clicking the heart button, and confirming the heart changes state and the paper appears in the favourites collection.

**Acceptance Scenarios**:

1. **Given** the user is on a paper detail page, **When** the paper is not yet in their favourites, **Then** an unfilled heart button is displayed on the page
2. **Given** the user is on a paper detail page and the paper is not in their favourites, **When** the user clicks the heart button, **Then** the heart button changes to a filled state and the paper is added to their favourites
3. **Given** the user is on a paper detail page and the paper is already in their favourites, **When** the user clicks the heart button, **Then** the heart button changes to an unfilled state and the paper is removed from their favourites
4. **Given** the user clicks the heart button and navigates to another page, **When** they return to the same paper detail page, **Then** the heart is still shown in the correct filled/unfilled state reflecting the saved status

---

### User Story 2 - Access Favourites via Hamburger Menu (Priority: P2)

A user who has saved papers wants to revisit them. They tap the hamburger icon (☰) visible in the header on every page. A navigation menu appears containing a "Favourites" option. They select it and are taken to a page listing all their saved papers, where they can click any entry to read the full detail.

**Why this priority**: The hamburger menu and Favourites page are the retrieval half of the feature. They depend on US1 (papers must be saveable first) but deliver the full user value once US1 is complete.

**Independent Test**: Can be fully tested (with at least one saved paper from US1) by clicking the hamburger icon, selecting "Favourites", and confirming saved papers are listed with working detail links.

**Acceptance Scenarios**:

1. **Given** any page in the application, **When** the user looks at the navigation header, **Then** a hamburger menu icon (☰) is visible
2. **Given** the hamburger icon is visible, **When** the user clicks it, **Then** a navigation menu appears containing a "Favourites" option
3. **Given** the user has saved at least one paper, **When** they navigate to the Favourites page via the hamburger menu, **Then** a list of their saved papers is displayed with each paper's title, authors, and a link to its full detail view
4. **Given** the user has no saved papers, **When** they navigate to the Favourites page, **Then** an "No favourites saved yet" is displayed.
5. **Given** the user is on the Favourites page, **When** they click on a paper's title or detail link, **Then** the full paper detail view is displayed correctly, even if the paper is no longer in the current search results
6. **Given** the user is on the Favourites page, **When** they click the remove control on a paper entry, **Then** the paper is removed from favourites and the Favourites page updates to show the paper is no longer saved

---

### Edge Cases

- What happens if a user favourites the same paper more than once? The second click removes it from favourites (toggle — no duplicates are stored).
- What happens to favourites when the browser session ends? Favourites are lost; they are stored for the duration of the browser session only.
- What happens when the Favourites list is empty and the user navigates to `/favourites`? "No favourites saved yet" is shown rather than a blank page.
- What happens if a user navigates directly to a paper detail URL from Favourites for a paper that is no longer in the current search results? The paper data stored in the favourites collection is used to render the detail view.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a heart button on every paper detail page
- **FR-002**: System MUST add the current paper to the user's favourites when the heart button is clicked and the paper is not already in favourites
- **FR-003**: System MUST remove the current paper from the user's favourites when the heart button is clicked and the paper is already in favourites (toggle behaviour)
- **FR-004**: System MUST display the heart button in a filled state when the current paper is in the user's favourites, and in an unfilled state when it is not
- **FR-005**: System MUST persist the user's favourites collection across page navigation within the same browser session
- **FR-006**: System MUST display a hamburger menu icon (☰) in the navigation header on all pages of the application
- **FR-007**: System MUST reveal a navigation menu containing a "Favourites" option when the hamburger icon is activated
- **FR-008**: System MUST provide a Favourites page (at a dedicated route) that lists all saved papers in reverse chronological order — most recently added paper displayed at the top
- **FR-009**: System MUST display each saved paper's title, authors, and a link to its full detail view on the Favourites page
- **FR-010**: System MUST display "No favourites saved yet" on the Favourites page when no papers have been saved
- **FR-011**: System MUST render the full paper detail view using data stored in the favourites collection when the paper is no longer present in the current search results
- **FR-012**: System MUST display a remove control (× button) on each paper entry on the Favourites page; clicking it removes that paper from favourites and the list updates immediately

### Key Entities *(include if feature involves data)*

- **Favourite**: A saved paper entry containing all data required to render the full detail view (title, authors, summary, URL, published date, source label). Belongs to the user's session-scoped favourites collection.
- **Favourites Collection**: The ordered set of all papers saved by the user in the current browser session, sorted most recently added first. Uniquely identified by paper ID; no duplicates.
- **Hamburger Menu**: A navigation component in the header that reveals app-level navigation options including "Favourites".

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can save any paper to favourites in a single click from the detail page
- **SC-002**: The favourites collection correctly reflects all add and remove actions within the same browser session, with the most recently saved paper appearing at the top of the list
- **SC-003**: Users can reach their favourites list from any page in the app in 2 clicks or fewer (hamburger icon → Favourites)
- **SC-004**: All saved papers on the Favourites page have working detail links and a remove control that correctly removes the paper from the list in one click
- **SC-005**: The heart button on the detail page accurately reflects the current saved/unsaved state on every visit within the session

## Assumptions

- Favourites are stored in the server-side browser session (using a session cookie) — data persists across page navigation but resets when the browser session ends
- No external database or persistent storage is required for this feature
- The hamburger menu is accessible to all users with no authentication requirement
- The heart button is only available on the paper detail page, not on the home page paper cards
- The Favourites page is a new, dedicated route in the application
- The hamburger menu requires a minimal amount of interactivity (toggle show/hide); a CSS-only or lightweight approach is acceptable
- The paper data stored in favourites includes all fields needed to re-render the full detail view without re-fetching from arXiv
- A reasonable upper bound of saved papers per session (~100) has no meaningful performance impact
