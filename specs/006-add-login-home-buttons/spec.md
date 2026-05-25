# Feature Specification: Add Login and Home Button

**Feature Branch**: `006-add-login-home-buttons`
**Created**: 2026-05-25
**Status**: Draft
**Input**: User description: "Add login and home button"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Registered User Logs In (Priority: P1)

A registered, verified user visits the login page, enters their email and password, and is signed in. The navigation reflects their authenticated state. On failure, a clear error message is shown without exposing which field was wrong.

**Why this priority**: Registration already exists but provides no ongoing value without login. This is the core authentication payoff for the existing registration flow.

**Independent Test**: Navigate to `/login`, submit valid credentials for a verified account, confirm redirect to the home page with authenticated state visible in the nav. Submitting wrong credentials leaves the user on `/login` with an error message.

**Acceptance Scenarios**:

1. **Given** a verified account exists, **When** the user submits the correct email and password, **Then** they are redirected to the home page and the nav replaces the "Login" link with a "Log out" button.
2. **Given** a user submits an incorrect password or an email that does not exist, **When** the form is submitted, **Then** a generic error is shown (no hint about which field was wrong) and the email field is pre-filled.
3. **Given** a user is already logged in, **When** they navigate to `/login`, **Then** they are redirected to the home page.
4. **Given** a logged-in user clicks the "Log out" button, **When** the logout request is processed, **Then** their session is destroyed, the nav shows the "Login" link, and they land on the home page.

---

### User Story 2 — Home Button Visible on Every Page (Priority: P2)

Any visitor (authenticated or not) can return to the home page from any page in the app via a visible "Home" link in the navigation.

**Why this priority**: The current nav has no consistent way to reach the home page from detail, register, check-email, or verify pages. This is a baseline usability gap that affects all users regardless of login state.

**Independent Test**: Open each non-home page (`/register`, `/check-email`, `/detail/<id>`, `/verify`). Confirm a "Home" link appears in the nav on every page and navigates to `GET /`.

**Acceptance Scenarios**:

1. **Given** a user is on the detail page, **When** they click "Home" in the nav, **Then** they are taken to `GET /`.
2. **Given** a user is on the register page, **When** they click "Home" in the nav, **Then** they are taken to `GET /`.
3. **Given** any page in the app, **When** it renders, **Then** the "Home" link is always visible in the nav.

---

### Edge Cases

- Blank email or password fields on login submission are treated as failed login — the same generic error from FR-005 applies.
- An email that was never registered produces the same generic error as wrong credentials (FR-005).
- If the user's session expires while browsing, the nav naturally reverts to unauthenticated state ("Login" link visible); no explicit redirect is required.
- Authenticated users visiting `/register` are redirected to home (FR-007).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The navigation MUST include a visible "Home" link on every page that navigates to `GET /`.
- **FR-002**: The app MUST provide a login page at `/login` with an email field and a password field.
- **FR-003**: The system MUST authenticate users by checking the submitted email and password against stored credentials.
- **FR-004**: On successful login, the system MUST create a persistent user session and redirect the user to the home page.
- **FR-005**: On failed login (wrong credentials, non-existent email), the system MUST display a user-friendly error message; wrong credentials MUST NOT reveal whether the email or password was incorrect.
- **FR-006**: Unverified (pending) accounts that attempt to log in shall be considered as invalid credential.
- **FR-007**: Users who are already authenticated and visit `/login` or `/register` MUST be redirected to the home page.
- **FR-008**: The navigation MUST show a "Login" link to unauthenticated users; for authenticated users the "Login" link MUST be replaced by a "Log out" button (no user identity information is displayed in the nav).
- **FR-009**: A `POST /logout` route MUST destroy the user session and redirect to the home page.

### Key Entities

- **UserSession**: Represents a verified user's authenticated state within a browser session; tied to a `UserAccount` with status `active`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A verified user can complete the full login flow (open `/login`, submit credentials, land on home page) in under 60 seconds.
- **SC-002**: A "Home" navigation link is present and functional on 100% of app pages.
- **SC-003**: Failed login attempts never reveal whether the email or the password was incorrect.
- **SC-004**: Authenticated users see their login state reflected in the nav on every page without needing to reload.

## Assumptions

- Login applies only to users who have already completed the email-verification flow (feature 002); no new account creation logic is in scope.
- A "Log out" route is considered in scope alongside "Log in" — it would be impractical to add login without logout.
- Session persistence follows the existing Flask session mechanism already in use for the registration flow.
- No "Remember me" / long-lived token functionality is in scope for this feature.
- The home button is a nav link (`/`), not a browser back button or JavaScript history action.
- Only Gmail accounts are eligible for login (inheriting the existing registration constraint).

## Clarifications

### Session 2026-05-25

- Q: What should the navigation show for authenticated users? → A: A "Log out" button only — no user identity information displayed in the nav.
- Q: Should an already-authenticated user visiting `/register` be redirected to home? → A: Yes — redirect to home (same pattern as `/login`).
