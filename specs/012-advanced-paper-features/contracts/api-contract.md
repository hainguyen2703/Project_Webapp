# API Contract: Advanced Paper Features (v1)

**Feature**: 012-advanced-paper-features  
**Date**: 2026-06-10

## Scope

Defines externally observable behavior for the 5 advanced features: "Worth Reading" scoring, related papers, duplicate detection, notifications, and trend analytics.

## Technical Implementation Notes (non-contractual)

- **scikit-learn**: Used for TF-IDF + cosine similarity calculations
- **pandas**: Used for trend analytics data aggregation
- **APScheduler**: Used for periodic background notification checks
- **Strict TDD**: All implementation follows test-driven development workflow (FAILING TESTS FIRST!)

## Route: GET /detail/<paper_id>

Paper detail page with new sidebar and scoring.

### Behavior changes

- Each paper MUST display a 1-5 star "Worth Reading" score.
- Sidebar MUST show "Related Papers" section with content-similar papers.
- Related paper links MUST navigate to corresponding detail pages.

### Score components (visible in UI but not formal API)

- Recency score: based on published_at date
- Relevance score: based on user interests
- Popularity score: based on category paper volume

## Route: GET / and GET /discover

Listing pages with duplicate detection.

### Behavior changes

- Papers with same arXiv ID MUST show "Duplicate" badge.
- Badge MUST have tooltip explaining it's a duplicate.
- Existing ordering and filtering behavior remains unchanged.

## Route: GET /analytics (NEW)

Trend analytics page (authenticated only).

### Auth

- MUST be accessible only to signed-in users.
- Unauthenticated access redirects to login.

### Response content

Page MUST display:
- Paper count trends by category over time
- Top authors per category
- Hot keywords and trending topics
- Analytics data MUST be processed via pandas

## Notification Delivery Contract

### Periodic background job

- APScheduler MUST run periodic background job to check for new relevant papers
- Job frequency: Defaults to hourly (configurable)
- New papers matching user interests MUST generate PaperNotification records

### Login-time display

- On each user login, system MUST display any undismissed notifications
- Notifications MUST be shown in-app on page load after login

### Notification state

- Notifications MUST have is_read and is_dismissed flags
- Clicking notification marks it as read and navigates to paper
- Dismissing notification marks it as dismissed and removes from UI

## Paper Persistence Contract

### PaperSnapshot

- System MUST persist PaperSnapshot records when papers are fetched
- Snapshots MUST be used for trend analytics calculation
- Snapshots MUST include all metadata needed for scoring and similarity

## Related Papers Contract

### Similarity calculation

- Related papers MUST be determined by scikit-learn TF-IDF + cosine similarity on title + summary
- At least 3 related papers MUST be shown if available
- Similarity scores MUST be recalculated periodically or on-demand

## "Worth Reading" Score Contract

### Calculation

- Overall score = (0.4 * recency_score) + (0.35 * relevance_score) + (0.25 * popularity_score)
- Each component normalized to 0.0-5.0 range
- Overall score rounded to nearest 0.5 for star display

### Display

- MUST display as 1-5 stars
- MAY show component breakdown on hover/click
- MUST be recalculated when user interests change

## Duplicate Detection Contract

### Detection logic

- Duplicates are papers with identical arXiv ID
- arXiv ID normalization MUST be applied before comparison
- Multiple versions (v1, v2) of same paper are considered duplicates

### Badge display

- Badge MUST appear next to paper title in listings
- Badge MUST be visually distinct (e.g., yellow/orange label)
- Tooltip MUST explain duplicate status

## Compatibility constraints

- All existing routes and API contracts remain backward-compatible
- New /analytics route is additive only
- Existing auth/login/logout/register/favorites flows unchanged
- Existing paper listing and detail functionality preserved

