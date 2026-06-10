# Feature Specification: Advanced Paper Features

**Feature Branch**: `012-advanced-paper-features`

**Created**: 2026-06-09

**Status**: Draft

**Input**: User description: "Implement 5 advanced features to maximize the project's value. 1. Recommend related papers. 2. Detect duplicate or highly similar papers. 3. Send automated notifications when new relevant papers arrive. 4. Generate trend statistics and analytics by topic. 5. Calculate a 'worth reading' score (Chấm điểm paper đáng đọc) for each paper based on specific metrics."

## Clarifications

### Session 2026-06-09

- **Q**: For "Recommend related papers", what approach would you prefer? **A**: Content similarity (Compare paper titles/summaries using text similarity)
- **Q**: For "Detect duplicate/similar papers", what should be considered a duplicate? **A**: Same arXiv ID (Exact same paper)
- **Q**: For "Automated notifications for new papers", what notification method would you like? **A**: In-app notifications only
- **Q**: For "Trend statistics by topic", what kind of analytics would you find most useful? **A**: All of the above (Paper count trends, top authors, hot keywords)
- **Q**: For "Worth Reading Score", what metrics should we use? **A**: Balanced score (Recency + relevance + category popularity)
- **Q**: Where should related papers be shown? **A**: Sidebar on detail page
- **Q**: What should happen when duplicates are detected? **A**: Mark with badge
- **Q**: How often should the system check for new relevant papers? **A**: On each user login
- **Q**: Where should trend analytics be shown? **A**: Dedicated Analytics page
- **Q**: How should the 'Worth Reading' score be displayed? **A**: 1-5 stars

## User Scenarios & Testing

### User Story 1 - Worth Reading Score (Priority: P1)

A user views any paper and immediately sees a 1-5 star "Worth Reading" score that helps them decide if the paper is worth their time.

**Why this priority**: This is the most immediately visible and useful feature for every paper view. It adds value to the core paper browsing experience without requiring complex infrastructure.

**Independent Test**: Can be fully tested by viewing any paper detail page and verifying the 1-5 star score is displayed and calculated based on recency, relevance to user interests, and category popularity.

**Acceptance Scenarios**:

1. **Given** a signed-in user viewing a paper detail page, **When** the page loads, **Then** the paper shows a 1-5 star "Worth Reading" score
2. **Given** a paper published within the last week, **When** the score is calculated, **Then** it receives a higher recency bonus
3. **Given** a paper matching the user's saved interests, **When** the score is calculated, **Then** it receives a relevance bonus
4. **Given** a paper in a popular category, **When** the score is calculated, **Then** it receives a popularity bonus

---

### User Story 2 - Related Papers (Priority: P2)

A user views a paper detail page and sees a sidebar with recommended related papers based on content similarity of titles and summaries.

**Why this priority**: This enhances the paper discovery experience by helping users find more relevant papers when they're already interested in one. It builds on the existing detail page infrastructure.

**Independent Test**: Can be fully tested by opening any paper detail page and verifying the sidebar shows related papers based on text similarity.

**Acceptance Scenarios**:

1. **Given** a user viewing a paper detail page, **When** the page loads, **Then** a sidebar shows "Related Papers" section
2. **Given** a paper with title and summary, **When** related papers are computed, **Then** papers with similar content appear in recommendations
3. **Given** related papers in the sidebar, **When** user clicks one, **Then** it navigates to that paper's detail page

---

### User Story 3 - Duplicate Detection (Priority: P2)

A user browses search results or discover page and sees duplicate papers marked with a badge so they can avoid redundant reading.

**Why this priority**: Improves the quality of paper listings by making duplicates obvious, reducing user frustration from seeing the same paper multiple times.

**Independent Test**: Can be fully tested by searching for papers that might have duplicates and verifying duplicates are marked with a badge.

**Acceptance Scenarios**:

1. **Given** search results containing multiple entries with the same arXiv ID, **When** results are displayed, **Then** duplicates show a "Duplicate" badge
2. **Given** a duplicate paper with a badge, **When** user hovers over the badge, **Then** it shows a tooltip explaining it's a duplicate
3. **Given** a paper listing without duplicates, **When** displayed, **Then** no duplicate badges appear

---

### User Story 4 - Trend Analytics Page (Priority: P3)

A signed-in user navigates to a dedicated Analytics page to see paper count trends over time, top authors per topic, and hot keywords/trending topics.

**Why this priority**: Provides valuable insights but requires more infrastructure and a new page. Useful for power users but not essential for core functionality.

**Independent Test**: Can be fully tested by navigating to /analytics and verifying all trend visualizations are present and functional.

**Acceptance Scenarios**:

1. **Given** a signed-in user, **When** they navigate to /analytics, **Then** the analytics page loads with trend statistics
2. **Given** the analytics page, **When** viewed, **Then** it shows paper count trends by topic over time
3. **Given** the analytics page, **When** viewed, **Then** it shows top authors per topic
4. **Given** the analytics page, **When** viewed, **Then** it shows hot keywords and trending topics

---

### User Story 5 - New Paper Notifications (Priority: P3)

A signed-in user logs in and sees in-app notifications for new relevant papers that match their interests since their last visit.

**Why this priority**: Requires background checking infrastructure and notification persistence. High value but more complex to implement well.

**Independent Test**: Can be fully tested by logging in after new papers matching user interests have been published, and verifying notifications appear.

**Acceptance Scenarios**:

1. **Given** a signed-in user, **When** they log in, **Then** the system checks for new relevant papers since last login
2. **Given** new relevant papers found, **When** user logs in, **Then** in-app notifications are displayed
3. **Given** notifications shown, **When** user clicks a notification, **Then** it navigates to the paper detail page
4. **Given** a notification, **When** user dismisses it, **Then** it doesn't appear again

---

### Edge Cases

- What happens when a paper has no summary available for similarity calculation? System falls back to category-based recommendations only.
- How does system handle papers older than the available historical data for trend analytics? Shows available data and indicates when data starts.
- What if a user has no interests configured for relevance scoring? Uses only recency and category popularity for score calculation.
- How does system handle arXiv papers with multiple versions (v1, v2, etc.)? Treats them as the same paper for duplicate detection.
- What if no new papers are found since last login? No notifications are shown, no error state.

## Requirements

### Functional Requirements

- **FR-001**: System MUST calculate and display a 1-5 star "Worth Reading" score for every paper
- **FR-002**: The "Worth Reading" score MUST be based on: recency (how recently published), relevance (match to user interests), and category popularity
- **FR-003**: System MUST display related papers in the sidebar of the paper detail page
- **FR-004**: Related papers MUST be determined based on content similarity of paper titles and summaries
- **FR-005**: System MUST detect duplicate papers by matching arXiv IDs
- **FR-006**: Duplicate papers MUST be marked with a visible "Duplicate" badge in listings
- **FR-007**: System MUST check for new relevant papers matching user interests on each user login
- **FR-008**: System MUST display in-app notifications for new relevant papers found at login
- **FR-009**: System MUST provide a dedicated /analytics page showing trend statistics
- **FR-010**: The analytics page MUST show paper count trends by topic over time
- **FR-011**: The analytics page MUST show top authors per topic
- **FR-012**: The analytics page MUST show hot keywords and trending topics
- **FR-013**: System MUST persist notification state so dismissed notifications don't reappear
- **FR-014**: System MUST track user's last login time for determining new papers
- **FR-015**: Related paper recommendations MUST link to the respective paper detail pages

### Key Entities

- **PaperScore**: Represents the "Worth Reading" score for a paper, with components for recency, relevance, and popularity
- **PaperRelation**: Represents a similarity relationship between two papers, with similarity score
- **PaperNotification**: Represents an in-app notification for a new relevant paper, with read/dismissed state
- **TrendAnalytics**: Represents aggregated trend data including paper counts, top authors, and hot keywords by topic over time periods
- **UserSession**: Extended to track last login timestamp for each user

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of paper detail pages display the "Worth Reading" score within 1 second of page load
- **SC-002**: Related paper recommendations load within 2 seconds of viewing a paper detail page
- **SC-003**: Duplicate papers are detected and marked with badges in 95% of cases where duplicates exist
- **SC-004**: New paper notification check completes within 3 seconds of user login
- **SC-005**: Analytics page loads all trend visualizations within 5 seconds
- **SC-006**: 80% of users in usability testing report the "Worth Reading" score helps them decide which papers to read

## Assumptions

- Existing user interest preferences and authentication system will be reused
- Content similarity can be implemented with simple text comparison algorithms (TF-IDF or similar) within the existing tech stack
- arXiv API provides sufficient metadata for calculating category popularity and author statistics
- Historical paper data can be stored/retrieved for trend analytics (will need to extend paper persistence)
- Users have stable internet connectivity for accessing paper metadata and recommendations
- In-app notifications don't require immediate real-time delivery, only checking at login time is sufficient
- Mobile responsive design is out of scope for v1, but existing responsive patterns will be followed
- No external citation data is available, so score won't include citation metrics
