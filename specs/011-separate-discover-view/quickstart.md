# Quickstart: Separate Discover View

**Feature**: 011-separate-discover-view  
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

### 1) Route separation correctness

1. Open `/` and confirm Home view is shown.
2. Open `/discover` as authenticated user and confirm Discover view is shown.
3. Verify Home and Discover can be navigated directly and independently.

### 2) Discover access control

1. Sign out.
2. Attempt to open `/discover`.
3. Verify redirect to login.

### 3) Post-login landing behavior

1. Sign in successfully.
2. Verify landing route is `/` (Home).
3. Navigate to `/discover` explicitly and confirm access.

### 4) Behavior parity across Home and Discover

1. Execute same discovery query from `/` and `/discover`.
2. Verify search controls, result rendering, and manual override behavior are functionally identical.
3. Verify sparse/empty guidance appears consistently on both routes.

### 5) Session-only state synchronization

1. Enter query/filter state on Home.
2. Navigate to Discover within same session.
3. Verify state is synchronized.
4. Open another browser/session and verify synchronized state is not inherited.

### 6) Prerequisite enforcement consistency

1. Use authenticated account lacking required discovery prerequisites.
2. Open `/discover`.
3. Verify prerequisite flow behavior remains consistent with existing rules.

## Test commands

```bash
pytest tests/integration/test_login_flow.py tests/integration/test_discovery_flow.py
pytest tests/
```

## Planned file touchpoints

- `src/app.py` (add/adjust `/discover` route + shared discovery orchestration + session sync)
- `src/templates/base.html` (navigation and active route cues)
- `src/templates/home.html` (shared discovery behavior consistency)
- `src/templates/discover.html` (dedicated Discover view scaffold if needed)
- `tests/integration/test_login_flow.py` (post-login landing and discover auth redirects)
- `tests/integration/test_discovery_flow.py` (behavior parity and session sync)

## Expected outcomes

- Home and Discover are distinct routes with explicit navigation cues.
- `/discover` is authenticated-only and redirects unauthenticated users to login.
- Successful login lands on Home.
- Discovery behavior remains functionally identical across both routes.
- Home/Discover query/filter synchronization is session-scoped only.

## Validation run notes

- Date: 2026-06-09
- Command executed: `d:/Project_CNPM/Project_Webapp/.venv/Scripts/python.exe -m pytest tests/integration/test_login_flow.py tests/integration/test_discovery_flow.py`
- Result: `27 passed`
- Command executed: `d:/Project_CNPM/Project_Webapp/.venv/Scripts/python.exe -m pytest tests/`
- Result: `51 passed`
- Coverage notes:
	- `/discover` route auth gating and onboarding prerequisite behavior validated.
	- Route-split parity validated for Home and Discover search/result paths.
	- Session-only query synchronization validated between `/` and `/discover`.
	- Active navigation cues and post-login landing behavior validated.
