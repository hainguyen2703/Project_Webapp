# Quickstart: Interest-Based Discover

**Feature**: 010-interest-discovery  
**Date**: 2026-06-09

## Prerequisites

- Python 3.x
- pip

## Setup

```bash
cd d:/Project_CNPM/Project_Webapp
pip install -r requirements.txt
```

## Run application

```bash
python -m src.app
```

App URL: http://localhost:8000

## Validation scenarios

### 1) Personalized default discover for onboarded user

1. Sign in with a user that has completed onboarding and at least 3 active interests.
2. Open home/discover and trigger fetch with no manual query.
3. Verify results are personalized from user interests and active interests are visible in UI context.

### 2) Relevance then recency ordering

1. Use an account with multiple interests that can match overlapping categories.
2. Trigger default discover with no manual query override.
3. Verify items are ordered by interest relevance first and recency second.

### 3) Immediate update reflection

1. As onboarded user, update interests via `/interests`.
2. Return to Discover and fetch with no manual query.
3. Verify the next Discover load reflects the updated interests immediately.

### 4) Sparse-match backfill behavior

1. Use niche interests that produce fewer direct matches than minimum display count.
2. Trigger default discover with no manual query.
3. Verify direct matches appear first, then broader recent backfill items fill to minimum count.
4. Verify sparse/backfill state messaging is clear.

### 5) Retired-interest reconciliation

1. Simulate retire of one or more currently selected interests.
2. Trigger request lifecycle for authenticated user.
3. Verify retired interests are removed and default interests auto-fill until effective interest count is at least 3.

### 6) Privacy isolation

1. Sign in as User A and capture active-interest context in Discover.
2. Sign out and sign in as User B.
3. Verify User A context and defaults are not visible/applied for User B.

### 7) Onboarding prerequisite remains enforced

1. Sign in as authenticated user without completed onboarding.
2. Open home/discover routes.
3. Verify redirect to `/onboarding/interests` and no personalized discover defaults are applied.

## Test commands

```bash
pytest tests/unit/test_interest_preferences.py tests/integration/test_discovery_flow.py
pytest tests/integration/test_login_flow.py tests/unit/test_source_clients.py
pytest tests/
```

## Planned file touchpoints

- `src/app.py` (discover default orchestration and context flags)
- `src/services/discovery_service.py` (ranking + sparse backfill logic)
- `src/services/db.py` (effective-interest reconciliation/default-fill helpers)
- `src/templates/home.html` (active-interest visibility and sparse-state messaging)
- `tests/integration/test_discovery_flow.py` (default behavior, ordering, backfill)
- `tests/unit/test_interest_preferences.py` (retired-interest and minimum restoration)

## Expected outcomes

- Discover defaults for onboarded users are interest-driven with OR eligibility.
- Ordering is deterministic: relevance first, recency second.
- Sparse direct-match sets are backfilled to minimum count without breaking UX.
- Interest updates are reflected on next Discover load.
- Cross-user interest context leakage remains zero in validation tests.

## Validation run notes

- Date: 2026-06-09
- Command executed: `d:/Project_CNPM/Project_Webapp/.venv/Scripts/python.exe -m pytest tests/integration/test_discovery_flow.py tests/unit/test_interest_preferences.py`
- Result: `17 passed`
- Command executed: `d:/Project_CNPM/Project_Webapp/.venv/Scripts/python.exe -m pytest tests/`
- Result: `46 passed`
- Coverage notes:
	- Personalized default Discover behavior verified for authenticated onboarded users.
	- Active-interest visibility and sparse backfill guidance verified in rendered Discover UI flow.
	- Retired-interest reconciliation and effective-interest context validation verified in unit tests.
	- Full regression suite passed with no detected authentication, registration, or source-client regressions.
