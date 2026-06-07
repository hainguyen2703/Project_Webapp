# Quickstart: User-Owned Favourites

**Feature**: 008-user-owned-favourites  
**Date**: 2026-06-07

## Prerequisites

- Python 3.x
- pip

## Setup

```bash
cd d:/Project_Webapp
pip install -r requirements.txt
```

## Run Application

```bash
python -m src.app
```

App URL: http://localhost:8000

## Validation Scenarios

### 1) Authenticated user can save and retain favourites across sessions

1. Register and log in as User A.
2. Fetch papers and open a detail page.
3. Add the paper to favourites.
4. Log out and log back in as User A.
5. Open favourites and verify the saved paper is still present.

### 2) Per-user isolation

1. While logged in as User A, save one paper.
2. Log out, then log in as User B.
3. Open favourites.
4. Verify User B does not see User A's saved paper.

### 3) Unauthenticated visibility and access constraints

1. Log out.
2. Verify favourites navigation is hidden from primary navigation.
3. Navigate directly to `/favourites`.
4. Verify response is a generic not-found page.

### 4) Duplicate prevention with canonical key

1. Log in as a user.
2. Save a paper once, then trigger add/save for the same `(source, external_paper_id)` again.
3. Verify only one favourite record exists for that user/paper pair.

### 5) Ordering and remove flow

1. Save Paper X, then save Paper Y.
2. Open favourites and verify order is Y then X (most recent first).
3. Remove Paper Y and verify only X remains.

### 6) Account deletion cleanup behavior

1. Create/save favourites under a user account.
2. Delete that account via admin/service path.
3. Verify all favourites tied to that `user_id` are removed immediately.

## Test Commands

```bash
pytest tests/unit/test_auth_service.py tests/unit/test_registration_service.py
pytest tests/integration/test_login_flow.py tests/integration/test_discovery_flow.py
pytest tests/
```

## Planned File Touchpoints

- `src/services/db.py` (favourites table + indexes + CRUD)
- `src/app.py` (auth gating + favourite route behavior + ownership wiring)
- `src/templates/base.html` (hide favourites navigation when logged out)
- `src/templates/detail.html` (auth-aware favourite affordance)
- `src/templates/favourites.html` (ordered list + empty state)
- `tests/integration/test_discovery_flow.py` (owned favourites flows)
- `tests/integration/test_login_flow.py` (auth visibility/access behavior)

## Implementation Entry Points and Ownership Mapping

- Route handlers and auth gating: `src/app.py`
- Favourites persistence, uniqueness, ordering, and deletion cleanup: `src/services/db.py`
- Navigation visibility logic for authenticated/unauthenticated users: `src/templates/base.html`
- Detail-page favourite toggle payload and state affordance: `src/templates/detail.html`
- Favourites list rendering and remove action wiring: `src/templates/favourites.html`
- Regression coverage for discovery + favourites flows: `tests/integration/test_discovery_flow.py`
- Regression coverage for login + access behavior: `tests/integration/test_login_flow.py`

## Expected Outcomes

- Favourites are owned by authenticated users and persist across sessions.
- No user can view or mutate another user's favourites.
- Duplicate favourites are prevented by `(source, external_paper_id)` per user.
- Logged-out users neither see favourites navigation nor access favourites routes.
- Favourites are listed most-recent-first and removed immediately on account deletion.

## Validation Log

- Date: 2026-06-07
- Command: `d:/Project_Webapp/.venv/Scripts/python.exe -m pytest tests/`
- Result: 42 passed, 0 failed
