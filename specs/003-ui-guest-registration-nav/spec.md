# Feature Specification: UI Guest & Registration Navigation

**Feature Branch**: `003-ui-guest-registration-nav`  
**Created**: 2026-05-15  
**Status**: Draft  
**Input**: User description: "Update UI to add the registration as an option in Dropdown menu. Registration is not mandatory for user. As guess, user cannot access to full feature which will be developed in future"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Access the site as a guest without registering (Priority: P1)

A visitor arrives at the paper discovery site and uses it without creating an account. They can browse papers and articles freely. No registration prompt blocks their experience, but the navigation clearly shows an option to sign up.

**Why this priority**: Most visitors will be guests. Ensuring the site is fully usable without registration is the primary guarantee that registration remains optional — and it is testable immediately without any auth infrastructure.

**Independent Test**: Open the site without being signed in. Confirm all current features (source selection, paper listing, detail view) work normally. Confirm the navigation dropdown is visible and contains a "Register" option. Confirm no feature is blocked or hidden that was previously accessible to all visitors.

**Acceptance Scenarios**:

1. **Given** a visitor opens the site without an account, **When** the page loads, **Then** all existing paper discovery features are accessible and no registration gate is shown.
2. **Given** a visitor is using the site as a guest, **When** they look at the navigation area, **Then** they see a dropdown menu containing at least a "Register" option.

---

### User Story 2 - Navigate to registration from the dropdown (Priority: P2)

A guest visitor decides they want to create an account. They find the "Register" option in the navigation dropdown and are taken to the registration page.

**Why this priority**: The dropdown is the primary entry point to the registration flow. Without this, the registration feature built in 002 has no navigation surface in the UI.

**Independent Test**: Click the "Register" item in the navigation dropdown. Confirm the user lands on the registration page (`/register`). Confirm navigating back from the registration page returns the user to the site in guest mode.

**Acceptance Scenarios**:

1. **Given** a guest is on any page of the site, **When** they open the navigation dropdown and select "Register", **Then** they are navigated to the registration page.
2. **Given** a visitor is on the registration page, **When** they navigate back (e.g., browser back or a back link), **Then** they return to the site in guest mode with no loss of context.
3. **Given** a guest views the page header, **When** they look at the navigation area, **Then** they see a hamburger icon (☰) labelled "Menu" that opens a dropdown containing a "Register" item when clicked.

---

### Edge Cases

- What happens when a registered user visits and is not yet signed in (pending or active account)? For this feature, all non-signed-in users are treated identically as guests — account status is irrelevant until a sign-in flow is built.
- What happens if the dropdown is opened on a slow connection before styles load? The dropdown must not cause a layout shift that obscures core page content.
- What happens on a very small desktop viewport? The dropdown must remain accessible; no clipping or overflow that hides the "Register" link.
- What happens if a user navigates directly to a future-feature URL that does not exist yet? Those URLs return a standard 404; no special handling is required in this feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The site navigation MUST include a dropdown menu visible on all pages.
- **FR-002**: The dropdown MUST contain a "Register" item that navigates the user to the registration page (`/register`).
- **FR-003**: All existing paper discovery features (source selection, listing, detail view) MUST remain fully accessible to guests without any registration prompt or gate.
- **FR-004**: The dropdown MUST be accessible via a hamburger menu icon (☰) labelled "Menu" in the page header area, consistent with the existing site header style. The dropdown opens and closes on click/tap of the trigger; hover MUST NOT trigger it.
- **FR-005**: The site MUST NOT display any notice, banner, or messaging to guests about future features or account benefits.

### Key Entities

- **Navigation Dropdown**: A UI component in the site header that groups user-account-related actions and future-feature links. Visible on all pages to all visitors regardless of authentication status.
- **Guest Session**: The default state of any visitor who has not signed in. No persistent data or cookie is required; guest status is inferred from the absence of a signed-in session.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of existing paper discovery features remain accessible to a guest visitor after this change is deployed (no regression).
- **SC-002**: A guest visitor can reach the registration page from the navigation dropdown in 2 clicks or fewer from any page.
- **SC-003**: The navigation dropdown renders correctly on all desktop viewport widths supported by the existing site without overflow or clipping.

## Assumptions

- A sign-in flow does not exist yet; the dropdown will not include a "Sign in" item in this feature (to be added when sign-in is specified).
- Future feature items are not shown in the dropdown for this release; placeholder entries will be introduced when those features are specified.
- Registration (feature 002) is already implemented and reachable at `/register`; this feature only adds a navigation surface to it.
- The site remains desktop-targeted (consistent with the project scope); no mobile-specific dropdown behaviour is required.
- A signed-in user experience (showing account info, sign-out option, etc.) is out of scope for this feature and will be addressed when a sign-in flow is specified.

## Clarifications

### Session 2026-05-15

- Q: How should future feature entries appear in the dropdown? → A: Hidden entirely — no placeholder items in the dropdown; only "Register" is shown.
- Q: How does the navigation dropdown open? → A: Click-triggered — user clicks/taps a button to open and close the dropdown.
- Q: How are guests informed that future features will require an account? → A: They are not — no notice, banner, or messaging about future features is shown to guests.
- Q: What label or text appears on the dropdown trigger button in the header? → A: Hamburger menu icon (☰) with text label "Menu".
