# Feature Specification: User Interest Selection Onboarding

**Feature Branch**: `009-build-user-interest-onboarding`  
**Created**: 2026-06-08  
**Status**: Draft  
**Input**: User description: "Build user interest selection onboarding"

## Clarifications

### Session 2026-06-08

- Q: Should users be allowed to skip interest onboarding and enter discovery? → A: Block entry until onboarding is completed (no skip)
- Q: How should users choose interests during onboarding? → A: Users choose only from a predefined interest catalog
- Q: How should retired interests be handled for existing users? → A: Automatically remove retired interests from user profiles
- Q: How should discovery defaults match selected interests? → A: OR match (include papers matching any selected interest)
- Q: If retired-interest removal drops users below minimum interests, how should the system recover? → A: Auto-fill missing slots with system default interests

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select Interests During Onboarding (Priority: P1)

A newly registered or first-time signed-in user is guided through onboarding to select their topic interests before entering the main discovery experience.

**Why this priority**: This is the core value of the feature. Without onboarding interest capture, the system cannot personalize discovery for the user.

**Independent Test**: Sign in as a user without saved interests, complete onboarding by selecting required interests, and confirm onboarding is marked complete and the user reaches discovery.

**Acceptance Scenarios**:

1. **Given** a signed-in user has not completed onboarding, **When** they enter the app after authentication, **Then** they are shown the interest selection onboarding flow before normal discovery entry
2. **Given** a signed-in user is on interest selection onboarding, **When** they select the required number of interests and submit, **Then** their interests are saved to their account and onboarding is marked complete
3. **Given** a signed-in user has already completed onboarding, **When** they sign in again, **Then** they are not forced back through onboarding
4. **Given** a signed-in user has not completed onboarding, **When** they attempt to navigate directly to discovery routes, **Then** the system redirects them to onboarding until completion

---

### User Story 2 - Manage Interests After Onboarding (Priority: P2)

A signed-in user can revisit and update their selected interests at any time.

**Why this priority**: Interests can change over time. Users need ongoing control to keep personalization relevant.

**Independent Test**: Sign in as an onboarded user, open interest management, change selections, save, and confirm updated interests persist on next sign-in.

**Acceptance Scenarios**:

1. **Given** a signed-in user has existing interests, **When** they open interest management, **Then** their current selected interests are pre-populated
2. **Given** a signed-in user edits their interests and saves, **When** save succeeds, **Then** the updated interests replace prior selections for that user
3. **Given** a save attempt violates interest selection rules, **When** user submits, **Then** the system shows a clear validation message and does not persist invalid data

---

### User Story 3 - Apply Interests to Discovery Defaults (Priority: P3)

A signed-in user sees discovery defaults informed by their selected interests to reduce effort and increase relevance.

**Why this priority**: This turns collected interests into immediate user value by improving first content shown.

**Independent Test**: Sign in as an onboarded user with known interests and verify discovery defaults reflect those interests without manual query entry.

**Acceptance Scenarios**:

1. **Given** a signed-in user with saved interests opens discovery, **When** no manual query override is supplied, **Then** default discovery filters/starting results reflect the user's saved interests
2. **Given** a signed-in user updates interests, **When** they return to discovery, **Then** updated interests drive the new default discovery state
3. **Given** a signed-in user has no saved interests because onboarding was never completed, **When** they access post-auth entry, **Then** onboarding is shown instead of personalized discovery defaults

---

### Edge Cases

- What happens when a user attempts to submit onboarding without meeting minimum selections? The system blocks submission and shows actionable validation feedback.
- What happens when a user tries to select beyond the allowed maximum interests? Additional selections are prevented until count is within allowed limits.
- What happens if a user abandons onboarding midway and returns later? Previously saved in-progress selections are restored only if explicitly saved; otherwise the user restarts from the persisted account state.
- What happens when a user account is deleted? Associated interest preferences are deleted with the account.
- What happens if a user tries to bypass onboarding by directly opening discovery endpoints? The system blocks discovery access and routes the user back to onboarding until onboarding is complete.
- What happens if a user enters a custom interest that is not in the catalog? The system rejects custom input and allows selection only from the predefined catalog.
- What happens when an interest is retired from the catalog? The retired interest is automatically removed from user profiles.
- What happens when retired-interest removal drops a user below the minimum selection count? The system auto-fills missing slots with system default interests to restore minimum coverage.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an interest selection onboarding flow for authenticated users who have not completed onboarding and block discovery access until onboarding is completed
- **FR-002**: System MUST require users to select at least 3 interests before onboarding can be completed
- **FR-003**: System MUST limit interest selection to a maximum of 10 interests per user
- **FR-004**: System MUST persist selected interests as account-owned user preferences
- **FR-005**: System MUST mark onboarding completion status per user account after valid submission
- **FR-006**: System MUST allow onboarding-complete users to revisit and update interests
- **FR-007**: System MUST pre-populate currently selected interests when users edit preferences
- **FR-008**: System MUST validate selection rules on save and return clear user-facing error messaging when invalid
- **FR-009**: System MUST apply saved user interests to discovery defaults when no manual override is provided
- **FR-010**: System MUST keep interest preferences isolated so users only view and edit their own preferences
- **FR-011**: System MUST ensure onboarding and interest management are accessible only to authenticated users and enforce onboarding as a required precondition for discovery access
- **FR-012**: System MUST remove stored user interests when the associated user account is deleted
- **FR-013**: System MUST allow interest selection only from the predefined interest catalog and reject custom free-text interest creation during onboarding and interest management
- **FR-014**: System MUST automatically remove interests from user profiles when those interests are retired from the catalog
- **FR-015**: System MUST apply interest-based discovery defaults using OR matching, where papers matching any selected interest are eligible
- **FR-016**: System MUST auto-fill missing interest slots with system default interests when retired-interest removal causes a user profile to fall below the minimum required interest count

### Key Entities *(include if feature involves data)*

- **Interest Topic**: A selectable category from a predefined product-managed catalog representing a user’s content preference domain (for example, AI, systems, theory), identified by a stable key and display label.
- **User Interest Preference Set**: The account-owned collection of selected interest topics for one user, including onboarding completion status and last-updated timestamp.
- **Onboarding State**: The per-user progress state indicating whether interest onboarding is required or completed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 95% of newly authenticated users complete interest onboarding in under 2 minutes
- **SC-002**: 99% of valid onboarding submissions persist successfully on first attempt
- **SC-003**: 95% of users who edit interests successfully save updated preferences on first attempt
- **SC-004**: 100% of discovery sessions without manual override for onboarded users apply account-saved interests as OR-based defaults
- **SC-005**: In multi-user validation tests, cross-user interest visibility or mutation incidents are 0

## Assumptions

- Existing account registration and login capabilities are already available and stable.
- A predefined catalog of selectable interest topics exists and is maintained by the product.
- Interest selection onboarding applies to signed-in users only and does not support anonymous sessions.
- Discovery can accept user preference defaults without changing the core query workflow.
