# Quickstart: User Login and Logout

**Feature**: 006-user-login-out  
**Date**: 2026-06-03

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

App URL: `http://localhost:8000`

## Validation Scenarios

### 1. Successful login

1. Ensure an account exists from registration flow.
2. Open `http://localhost:8000/login`.
3. Submit valid email/password.
4. Verify redirect to signed-in state and account-enabled access.

### 2. Invalid login handling

1. Submit missing email/password.
2. Verify login blocked with clear, non-sensitive message.
3. Submit incorrect credentials.
4. Verify no authenticated session is created.

### 3. Rapid failure throttling

1. Submit several invalid login attempts quickly.
2. Verify temporary throttling behavior appears.
3. Verify valid session is still not created during throttling period.

### 4. Logout behavior

1. While signed in, submit logout.
2. Verify all active sessions for that user are invalidated.
3. While signed out, call logout endpoint.
4. Verify request is blocked with 401/403 behavior and no session changes.

### 5. Session expiration behavior

1. Simulate an expired session.
2. Trigger a protected action.
3. Verify session auto-refresh occurs without forcing re-login.

## Test Commands

```bash
pytest tests/unit/test_auth_service.py
pytest tests/integration/test_login_flow.py
pytest tests/
```

## Planned Files

- `src/app.py`
- `src/services/auth_service.py`
- `src/services/db.py`
- `src/models/auth_user.py`
- `src/templates/login.html`
- `src/templates/base.html`
- `src/templates/home.html`
- `src/static/styles.css`
- `tests/unit/test_auth_service.py`
- `tests/integration/test_login_flow.py`

## Validation Log

- Date: 2026-06-03
- Environment: Python 3.13.2 virtual environment at d:/Project_Webapp/.venv
- Command: d:/Project_Webapp/.venv/Scripts/python.exe -m pytest tests/
- Result: 38 passed, 0 failed
