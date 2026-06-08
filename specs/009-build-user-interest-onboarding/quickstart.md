# Quickstart: User Interest Selection Onboarding

**Feature**: 009-build-user-interest-onboarding  
**Date**: 2026-06-08

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

### 1) Mandatory onboarding gate

1. Register/sign in as a user with no interest preferences.
2. Attempt to access discovery directly.
3. Verify user is redirected to interest onboarding until completion.

### 2) Valid onboarding save

1. Select 3 to 10 catalog interests.
2. Submit onboarding.
3. Verify onboarding is marked complete and user enters discovery.

### 3) Catalog-only enforcement

1. Attempt to submit a non-catalog/free-text interest payload.
2. Verify save is rejected with clear validation feedback.

### 4) Interest management updates

1. Open interest management as onboarded user.
2. Confirm current selections are pre-populated.
3. Update selection set within valid bounds and save.
4. Verify updates persist across sign-out/sign-in.

### 5) OR-based discovery defaults

1. Save multiple interests.
2. Open discovery with no manual override.
3. Verify defaults include papers matching any selected interest.

### 6) Retired interest handling and auto-fill

1. Retire one or more selected interests in catalog state.
2. Verify retired interests are removed from user profile.
3. If user falls below minimum, verify system default interests are auto-added.

### 7) Account deletion cleanup

1. Create user with completed onboarding and saved interests.
2. Delete account.
3. Verify preference metadata and selections are deleted.

## Test Commands

```bash
pytest tests/unit/test_auth_service.py tests/unit/test_registration_service.py
pytest tests/integration/test_login_flow.py tests/integration/test_discovery_flow.py
pytest tests/
```

## Validation Run Notes

- Date: 2026-06-08
- Command executed: `d:/Project_Webapp/.venv/Scripts/python.exe -m pytest tests/`
- Result: `42 passed`
- Coverage notes:
	- Onboarding gate redirect enforced for authenticated users without completed interests.
	- Onboarding and interest management routes validated for auth and selection bounds.
	- Discovery defaults validated to use OR category matching when no manual query is provided.
	- Manual query override validated to bypass interest-derived default query.
	- Retired-interest reconciliation and minimum auto-fill validated in unit tests.
	- Account deletion cleanup validated for favourite and interest-owned records.

## Planned File Touchpoints

- `src/services/db.py` (interest catalog + user preference persistence + cleanup)
- `src/app.py` (onboarding gate, save/update endpoints, discovery defaults)
- `src/templates/onboarding_interests.html` (new onboarding screen)
- `src/templates/interests.html` (new management screen)
- `src/templates/base.html` (authenticated navigation to interests)
- `src/templates/home.html` (default-interest discovery context)
- `tests/integration/test_login_flow.py` (onboarding gate coverage)
- `tests/integration/test_discovery_flow.py` (OR defaults and override behavior)

## Expected Outcomes

- Authenticated users without completed onboarding cannot access discovery.
- User interest preferences are account-owned, catalog-constrained, and persisted.
- Discovery defaults apply OR matching across selected interests when no manual override exists.
- Retired interests are auto-removed and minimum count is auto-restored via defaults.
