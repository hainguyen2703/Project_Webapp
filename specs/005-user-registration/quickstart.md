# Quickstart: User Registration

**Feature**: 005-user-registration  
**Date**: 2026-06-02

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

## Registration Scenarios

### 1. Successful registration

1. Open `http://localhost:8000/register`.
2. Submit:
   - Email: `new.user@example.com`
   - Password: `pass1234`
3. Verify redirect to home page with registration success message.
4. Confirm account is created as active in SQLite.

### 2. Password policy rejection

1. Open `/register`.
2. Submit password that does not meet policy (for example `abcdefg`).
3. Verify form re-renders with policy error and no account is created.

### 3. Duplicate email rejection

1. Register once with `duplicate@example.com`.
2. Submit registration again using same email.
3. Verify duplicate-email error and only one account row exists.

### 4. Whitespace rejection

1. Submit email with leading/trailing spaces (for example ` user@example.com `).
2. Verify request is rejected with validation error.

### 5. Rapid duplicate submission behavior

1. Submit the same form twice rapidly (same `submission_token`).
2. Verify only one successful account creation occurs.
3. Verify second in-flight submission is rejected/ignored.

## Test Commands

```bash
pytest tests/unit/test_registration_service.py
pytest tests/integration/test_registration_flow.py
pytest tests/
```

## Expected Files Added/Modified During Implementation

- `src/app.py`
- `src/services/db.py`
- `src/services/registration_service.py`
- `src/templates/register.html`
- `src/templates/base.html`
- `src/templates/home.html`
- `src/static/styles.css`
- `tests/unit/test_registration_service.py`
- `tests/integration/test_registration_flow.py`

## Validation Log

- Date: 2026-06-02
- Environment: Python 3.13.2 virtual environment at d:/Project_Webapp/.venv
- Command: d:/Project_Webapp/.venv/Scripts/python.exe -m pytest tests/
- Result: 28 passed, 0 failed
