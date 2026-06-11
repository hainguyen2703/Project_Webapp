# Quickstart: Advanced Paper Features

**Feature**: 012-advanced-paper-features  
**Date**: 2026-06-10

## Prerequisites

- Python 3.x
- pip

## Setup

```bash
cd d:/programming/codedocs/degree2/ThirdSemester/nmcnpm/Project_Webapp
pip install -r requirements.txt
# New dependencies (auto-installed via updated requirements.txt):
# - scikit-learn (for TF-IDF text similarity)
# - pandas (for trend analytics)
# - APScheduler (for background notification jobs)
```

## Run application

```bash
python -m src.app
```

App URL: http://localhost:8000

## Important TDD Workflow Reminder

**STRICT TDD - FAILING TESTS FIRST!**
1. Write the FAILING test first
2. Run the test to confirm it FAILS
3. Implement the minimal code to make it PASS
4. Refactor if needed

## Validation scenarios

### 1) "Worth Reading" score display

1. Search for any paper and open its detail page.
2. Verify 1-5 star "Worth Reading" score is displayed.
3. Check that score appears quickly (under 1 second).

### 2) Related papers sidebar

1. Open any paper detail page.
2. Verify sidebar shows "Related Papers" section.
3. Click a related paper and verify navigation to that paper's detail works.

### 3) Duplicate paper badges

1. Search or browse to results with papers having same arXiv ID.
2. Verify duplicates show "Duplicate" badge.
3. Hover over badge to see tooltip.

### 4) New paper notifications (background job)

1. Verify APScheduler background job is running on app startup.
2. Trigger a manual paper check (if applicable) or wait for scheduled run.
3. Sign out, then sign in again.
4. If new relevant papers exist, verify in-app notifications appear.
5. Click notification to navigate to paper, dismiss to remove.

### 5) Analytics page (pandas-based)

1. Navigate to `/analytics` as signed-in user.
2. Verify trend statistics display (paper counts, top authors, hot keywords).
3. Check page loads within 5 seconds.

## Test commands

```bash
# Run all tests (strict TDD workflow)
pytest tests/

# Run by category
pytest tests/unit/test_advanced_features.py  # Unit tests
pytest tests/integration/test_advanced_features_flow.py  # Integration tests
```

## Planned file touchpoints

- `src/models/article.py` (extend with score calculation helpers)
- `src/models/advanced_features.py` (new models: PaperScore, PaperRelation, PaperNotification, PaperSnapshot, CategoryStats, UserMetadata)
- `src/services/db.py` (extend DB with new tables and CRUD)
- `src/services/advanced_service.py` (new service: scoring, similarity, notification check, analytics with pandas)
- `src/services/scheduler_service.py` (new service: APScheduler setup and background jobs)
- `src/app.py` (add /analytics route, extend detail/listing/login routes, add APScheduler initialization)
- `src/templates/detail.html` (add sidebar for related papers, score display)
- `src/templates/home.html` / `discover.html` (add duplicate badges)
- `src/templates/analytics.html` (new template for analytics page)
- `src/templates/base.html` (add notification UI component)
- `src/static/styles.css` (styles for badges, stars, notifications)
- `requirements.txt` (add scikit-learn, pandas, APScheduler)
- `tests/unit/test_advanced_features.py` (new TDD unit tests)
- `tests/integration/test_advanced_features_flow.py` (new TDD integration tests)

## Expected outcomes

- All 5 advanced features are implemented and working.
- "Worth Reading" scores display and update correctly.
- Related paper recommendations load quickly.
- Duplicates are detected and badged properly.
- APScheduler background jobs periodically check for new papers.
- Notifications appear on login when new relevant papers exist.
- Analytics page (pandas-based) shows trends from historical data.
- No regressions in existing features (auth, search, favorites, interests).

## Validation run notes

- Date: 2026-06-10
- Status: Pending implementation
- Result: To be executed after implementation

