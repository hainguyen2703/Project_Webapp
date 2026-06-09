# Feature Specification: Interest-Based Discover

**Feature Branch**: `010-create-interest-discovery`  
**Created**: 2026-06-09  
**Status**: Draft  
**Input**: User description: "Creat \"Discover\" based on user interest"

## Clarifications

### Session 2026-06-09

- Q: What matching strategy should Discover use for interest-based defaults? → A: OR match with ranking by interest relevance first, then recency
- Q: How should Discover handle interests that become unavailable in the catalog? → A: Automatically remove unavailable interests and auto-fill with system defaults if below minimum
- Q: What minimum number of interests should be required for valid Discover personalization? → A: Minimum 3 interests
- Q: When should Discover apply saved interest updates? → A: Apply updates immediately on next Discover load
- Q: How should Discover populate sparse result sets? → A: Show direct matches first, then backfill with broader recent papers to a fixed minimum result count

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Personalized Discover Landing (Priority: P1)

A signed-in user opens Discover and immediately sees papers aligned with their saved interests, without needing to type a query.

**Why this priority**: This is the core value of the feature. If the first Discover view is not interest-aware, the experience remains generic and less useful.

**Independent Test**: Sign in with a user account that has known interest preferences, open Discover with no manual search input, and verify results are relevant to saved interests.

**Acceptance Scenarios**:

1. **Given** a signed-in user with saved interests, **When** they open Discover with no manual query, **Then** Discover shows papers matching any selected interest and ranks them by interest relevance first, then recency
2. **Given** a signed-in user with saved interests, **When** Discover loads default results, **Then** only that user’s own saved interests are used to determine defaults
3. **Given** a signed-in user updates interests, **When** they revisit Discover, **Then** default Discover results reflect updated interests

---

### User Story 2 - Transparent Interest Context (Priority: P2)

A user can see which interests are currently shaping their Discover results so they understand why specific content is shown.

**Why this priority**: Transparency increases trust and helps users decide whether they need to adjust interests.

**Independent Test**: Open Discover as a user with saved interests and verify the active interest context is clearly visible and matches account preferences.

**Acceptance Scenarios**:

1. **Given** a signed-in user with saved interests, **When** Discover loads, **Then** the page clearly displays the active interests driving default results
2. **Given** a signed-in user with no saved interests, **When** they enter Discover entry flow, **Then** the system clearly communicates that interests are required and routes them to interest setup

---

### User Story 3 - Stable Discovery Under Sparse Matches (Priority: P3)

A user still receives a usable Discover experience when exact interest matches are limited.

**Why this priority**: Discover should remain helpful even in low-signal conditions instead of appearing empty or broken.

**Independent Test**: Use an account with niche interests that produce few direct matches and verify Discover still returns a non-empty, clearly explained result set.

**Acceptance Scenarios**:

1. **Given** a signed-in user whose interests produce very few direct matches, **When** Discover loads, **Then** the system shows direct matches first and backfills with broader recent papers until a fixed minimum result count is reached
2. **Given** no results can be returned for current interests in the selected time window, **When** Discover loads, **Then** the system presents a clear empty-state message with guidance to update interests or broaden discovery

---

### Edge Cases

- A user has completed authentication but has not completed interest setup.
- A user has fewer than 3 effective interests and cannot enter normal interest-based Discover until minimum coverage is restored.
- A user has saved interests, but some interests are no longer available in the catalog; unavailable interests are removed automatically.
- Automatic removal can drop a user below the minimum valid interest count; missing slots are auto-filled with system defaults.
- A user’s interests are highly niche and produce very few matches.
- A user repeatedly refreshes Discover in a short period and should receive consistent defaults for the same preference state.
- A user account is switched (log out/log in as another user) and Discover must not carry over prior user interest context.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST personalize Discover default results for signed-in users using that user’s saved interest preferences with OR matching (papers matching any selected interest are eligible)
- **FR-002**: System MUST use only account-owned interests of the current signed-in user when determining Discover defaults
- **FR-003**: System MUST update Discover defaults after a user changes and saves interests
- **FR-004**: System MUST visibly show the active interests currently influencing Discover defaults
- **FR-005**: System MUST provide clear user messaging when interest-based defaults cannot be fully applied
- **FR-006**: System MUST present a usable fallback Discover result set when direct interest matches are sparse
- **FR-007**: System MUST provide an explicit empty-state with next-step guidance when no discoverable content can be returned
- **FR-008**: System MUST route authenticated users without completed interest setup to the interest setup flow before enabling normal interest-based Discover defaults
- **FR-009**: System MUST preserve user privacy by preventing exposure of one user’s interest context to another user
- **FR-010**: System MUST keep default Discover behavior consistent for the same user preference state within a single session
- **FR-011**: System MUST maintain discoverability even when interest catalog changes affect previously selected interests
- **FR-012**: System MUST rank default Discover results by interest relevance first and recency second
- **FR-013**: System MUST automatically remove unavailable interests from user preference context when those interests are retired from the catalog
- **FR-014**: System MUST auto-fill missing interest slots with system default interests when retired-interest removal causes the user to fall below the minimum required interest count
- **FR-015**: System MUST enforce a minimum of 3 effective interests for valid Discover personalization
- **FR-016**: System MUST apply saved interest updates immediately on the next Discover page load
- **FR-017**: System MUST show direct interest matches first and then backfill with broader recent papers to a fixed minimum default Discover result count when direct matches are sparse

### Key Entities *(include if feature involves data)*

- **Discover Preference Context**: The current signed-in user’s effective interest set used to derive default Discover results, including validity state and last-updated timestamp.
- **Discover Result Set**: The collection of content items shown on Discover for a given user context, including whether results are direct matches or fallback results.
- **Interest Visibility State**: User-facing representation of which interests are currently active in Discover defaults and whether any are unavailable.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 90% of signed-in users with configured interests see first Discover results in under 2 seconds after opening Discover
- **SC-002**: 95% of sampled Discover sessions for users with configured interests include results aligned with at least one saved interest
- **SC-003**: 95% of users who update interests see Discover defaults reflect their changes by the next Discover page load
- **SC-004**: In privacy validation tests, cross-user interest-context leakage incidents are 0
- **SC-005**: 85% of users in usability testing can correctly identify which interests are shaping Discover defaults without assistance

## Assumptions

- Interest preferences are already collected and stored per account through existing onboarding or profile flows.
- Discover is available only to authenticated users.
- Content metadata is sufficient to evaluate relevance against user interests.
- Existing account/session behavior determines the active signed-in user context for Discover.
