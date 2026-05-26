# Feature Specification: Simplify to arXiv-Only Source

**Feature Branch**: `003-arxiv-only-source`  
**Created**: 2026-05-26  
**Status**: Draft  
**Input**: User description: "Remove medium source, add 'Home' button and make arXiv as only source paper, remove dropdown menu to select source paper"

## Clarifications

### Session 2026-05-26

- Q: Should Medium-related backend files (e.g., `medium_client.py`) be deleted or disabled? → A: Delete all Medium-related files entirely
- Q: Should the source attribution label be kept or removed after Medium is removed? → A: Keep "arXiv" as attribution label on paper cards and detail pages
- Q: What happens when the "Home" button is clicked while already on the home page? → A: Reload the page, refreshing the arXiv paper feed

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse arXiv Papers Directly (Priority: P1)

A user visits the paper discovery site and immediately sees a feed of arXiv papers without any source selection step. The interface is streamlined — there is no dropdown or selector asking which source to use.

**Why this priority**: This is the core change. Removing Medium and the dropdown is the primary scope of this feature and delivers immediate value by simplifying the user experience.

**Independent Test**: Can be fully tested by opening the home page and verifying only arXiv papers appear, with no source selector present, without any other changes to the app.

**Acceptance Scenarios**:

1. **Given** the user opens the home page, **When** the page loads, **Then** the paper feed displays only arXiv papers without any prompt to select a source
2. **Given** the paper list is displayed, **When** the user inspects the source information, **Then** all papers are attributed to arXiv and no Medium papers appear
3. **Given** any page in the application, **When** the user looks for a source-selection dropdown, **Then** no such control is visible or interactive

---

### User Story 2 - Navigate Back to Home via Home Button (Priority: P2)

A user who is on a paper detail page or any secondary page wants to return to the main paper listing. A clearly visible "Home" button provides one-click navigation back to the home page.

**Why this priority**: Navigation improvement that complements the simplified source flow. Without a source dropdown, the Home button becomes the primary navigation anchor.

**Independent Test**: Can be fully tested by navigating to a paper detail page and clicking the "Home" button, verifying it returns to the home/listing page.

**Acceptance Scenarios**:

1. **Given** the user is on the paper detail page, **When** they click the "Home" button, **Then** they are taken to the main paper listing page
2. **Given** any page in the application, **When** the user looks for navigation, **Then** a "Home" button is visible in the navigation area
3. **Given** the user is already on the home page, **When** they click the "Home" button, **Then** the arXiv paper feed reloads and displays a fresh set of results

---

### Edge Cases

- What happens when arXiv returns no results? The user should see a clear "no results" message rather than an empty page.
- What happens if arXiv is temporarily unavailable? The user should see a user-friendly error message.
- What happens to any existing bookmarked URLs that included a source parameter for Medium? They should gracefully fall back to the arXiv-only listing.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST remove Medium as a paper discovery source from the application
- **FR-002**: System MUST display only arXiv papers in the paper discovery feed
- **FR-003**: System MUST remove the source-selection dropdown menu from all pages
- **FR-004**: System MUST display a "Home" button visible on all pages of the application
- **FR-005**: System MUST navigate the user to the main paper listing page when the "Home" button is clicked; if already on the home page, the arXiv paper feed MUST reload
- **FR-006**: System MUST delete all Medium-related source files (e.g., `medium_client.py`, any Medium service or configuration code) — not just disable or comment them out
- **FR-007**: System MUST preserve all existing arXiv paper discovery functionality after the changes
- **FR-008**: System MUST display "arXiv" as the source attribution label on all paper cards and detail pages

### Key Entities *(include if feature involves data)*

- **Paper Source**: Previously had multiple values (arXiv, Medium); after this change, only arXiv is valid
- **Navigation**: A "Home" control that links back to the root/listing page

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users reach the arXiv paper feed in one step (directly on page load) with no source selection required
- **SC-002**: Zero Medium-sourced papers or Medium-related UI elements appear anywhere in the application
- **SC-003**: A "Home" button is visible on 100% of application pages
- **SC-004**: Users can return to the main listing from any page in a single click via the "Home" button
- **SC-005**: All existing arXiv paper discovery results and functionality remain unchanged after the source simplification

## Assumptions

- The application currently supports both arXiv and Medium as paper sources
- A source-selection dropdown currently exists in the UI for choosing between sources
- The "Home" button should appear in the top navigation or header area, visible on all pages
- Removing Medium means physically deleting all Medium-specific files (`medium_client.py`, Medium service code) and any UI or configuration references — no dead code is left behind
- The arXiv source configuration and behavior remain intact and unchanged
- No new paper sources are being added as part of this feature
