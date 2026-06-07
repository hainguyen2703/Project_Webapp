# Feature Specification: User-Owned Favourites

**Feature Branch**: `008-user-owned-favourites`  
**Created**: 2026-06-07  
**Status**: Draft  
**Input**: User description: "Favourites belong to users"

## Clarifications

### Session 2026-06-07

- Q: How should unauthenticated users experience favourites access? → A: Hide favourites navigation when logged out; direct URL access shows generic not-found
- Q: What uniqueness key defines one favourite per user? → A: Use source + external paper ID
- Q: What happens to favourites when a user account is deleted? → A: Delete all favourites immediately when the user account is deleted
- Q: In what order should favourites be displayed? → A: Most recently added first

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Save Favourites to Account (Priority: P1)

An authenticated user viewing a paper can save it to their favourites, and that saved item is tied to their own account.

**Why this priority**: This is the core value of the feature. Without account-owned saving, favourites cannot reliably persist for an individual user.

**Independent Test**: Log in as a user, save a paper as favourite, sign out and sign back in as the same user, and confirm the paper remains in that user's favourites.

**Acceptance Scenarios**:

1. **Given** a logged-in user is viewing a paper detail page, **When** they choose to save the paper as a favourite, **Then** the paper is added to that user's favourites list
2. **Given** a logged-in user has already saved a paper, **When** they try to save the same paper again, **Then** the system prevents duplicate entries in that user's favourites list
3. **Given** a user is not logged in, **When** they try to save a favourite, **Then** the system asks them to sign in before saving

---

### User Story 2 - View and Manage Own Favourites (Priority: P2)

A logged-in user can view and remove items from their own favourites list without affecting any other user's list.

**Why this priority**: Users must be able to curate their own saved content; otherwise favourites quickly become stale and less useful.

**Independent Test**: Log in as a user with saved favourites, open favourites, remove one paper, and confirm the list updates and reflects the removal on the next visit.

**Acceptance Scenarios**:

1. **Given** a logged-in user has at least one saved favourite, **When** they open their favourites list, **Then** only their own saved papers are shown
2. **Given** a logged-in user has a saved favourite, **When** they remove it from favourites, **Then** the item is removed from that user's favourites list
3. **Given** a logged-in user has no saved favourites, **When** they open the favourites list, **Then** they see an empty-state message

---

### User Story 3 - Keep User Favourites Isolated (Priority: P3)

Different users should never see or modify each other's favourites.

**Why this priority**: Account-level data isolation is essential for trust, privacy, and correct multi-user behavior.

**Independent Test**: Save favourites under User A, sign in as User B, and verify User B cannot see or alter User A's favourites.

**Acceptance Scenarios**:

1. **Given** User A has saved favourites, **When** User B signs in and opens favourites, **Then** User B does not see User A's favourites
2. **Given** User A and User B have both saved favourites, **When** User A removes a favourite, **Then** User B's favourites remain unchanged
3. **Given** a user signs out, **When** another user signs in on the same device, **Then** the newly signed-in user sees only their own favourites

---

### Edge Cases

- What happens when a user attempts to favourite a paper that was previously removed from their list? The paper can be re-added as a new favourite for that user.
- How does the system behave when a user account has no favourites yet? The system shows a clear empty state for authenticated users.
- What happens if two users save the same paper? Each user's favourites contain their own independent entry for that paper reference.
- What happens when an unauthenticated user navigates to favourites? The favourites navigation is hidden when logged out, and direct URL access returns a generic not-found page.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow authenticated users to save a paper to favourites
- **FR-002**: System MUST associate each favourite with exactly one user account
- **FR-003**: System MUST prevent duplicate favourites for the same user using the tuple (source, external_paper_id) as the paper uniqueness key
- **FR-004**: System MUST allow authenticated users to remove papers from their own favourites
- **FR-005**: System MUST show each user only the favourites associated with their own account
- **FR-006**: System MUST keep favourites available to the same user across sessions until the user removes them
- **FR-007**: System MUST require sign-in before a user can add or remove account-owned favourites
- **FR-008**: System MUST show a clear empty state when a logged-in user has no favourites
- **FR-009**: System MUST ensure actions on one user's favourites never modify another user's favourites
- **FR-010**: System MUST preserve favourites ownership correctly when users sign out and another user signs in on the same device
- **FR-011**: System MUST hide favourites navigation for unauthenticated users and return a generic not-found response for unauthenticated direct access to favourites routes
- **FR-012**: System MUST delete all favourites owned by a user immediately when that user account is deleted
- **FR-013**: System MUST display each user's favourites in descending created-at order (most recently added first)

### Key Entities *(include if feature involves data)*

- **User**: A registered account holder who can sign in and maintain a personal favourites list.
- **Favourite**: A saved paper reference owned by one user, including source and external_paper_id plus the minimum paper details needed to list and reopen the item.
- **Paper Reference**: The identifying metadata for a discovered paper used when saving and displaying favourites; uniquely identified by (source, external_paper_id).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of favourites displayed to a user belong to that signed-in user in multi-user validation tests
- **SC-002**: 95% of authenticated users can save a paper to favourites in one action on first attempt
- **SC-003**: 95% of authenticated users can remove a saved favourite in one action on first attempt
- **SC-004**: Returning users can access previously saved favourites in under 10 seconds after sign-in
- **SC-005**: In role-switch testing on the same device, cross-user favourites visibility incidents are 0

## Assumptions

- User registration and sign-in are already available in the product.
- Users are expected to be authenticated before using account-owned favourites features.
- Existing paper discovery and detail views remain unchanged except for ownership behavior of favourites.
- Historical anonymous or session-only favourites are out of scope for this feature unless explicitly migrated later.
- Account deletion capability exists and triggers immediate cleanup of user-owned favourites.
