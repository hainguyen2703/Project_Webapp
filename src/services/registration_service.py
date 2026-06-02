from __future__ import annotations

import re
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Union

from werkzeug.security import check_password_hash, generate_password_hash

from src.services.db import get_connection

IN_FLIGHT_TTL_SECONDS = 15.0
IN_FLIGHT_SUBMISSIONS: Dict[str, float] = {}
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


@dataclass
class RegistrationResult:
    success: bool
    code: str
    errors: Dict[str, str] = field(default_factory=dict)
    user_id: Optional[int] = None


def generate_submission_token() -> str:
    return secrets.token_urlsafe(24)


def reset_submission_locks() -> None:
    IN_FLIGHT_SUBMISSIONS.clear()


def _lock_key(session_key: str, submission_token: str) -> str:
    return f"{session_key}:{submission_token}"


def purge_expired_submissions(now: Optional[float] = None) -> None:
    current = now if now is not None else time.time()
    stale_keys = [
        key for key, timestamp in IN_FLIGHT_SUBMISSIONS.items() if current - timestamp > IN_FLIGHT_TTL_SECONDS
    ]
    for key in stale_keys:
        IN_FLIGHT_SUBMISSIONS.pop(key, None)


def acquire_submission_lock(session_key: str, submission_token: str) -> bool:
    purge_expired_submissions()
    key = _lock_key(session_key, submission_token)
    if key in IN_FLIGHT_SUBMISSIONS:
        return False
    IN_FLIGHT_SUBMISSIONS[key] = time.time()
    return True


def release_submission_lock(session_key: str, submission_token: str) -> None:
    IN_FLIGHT_SUBMISSIONS.pop(_lock_key(session_key, submission_token), None)


def password_meets_policy(password: str) -> bool:
    if len(password) < 8:
        return False
    has_letter = any(char.isalpha() for char in password)
    has_number = any(char.isdigit() for char in password)
    return has_letter and has_number


def validate_registration_input(email: str, password: str) -> Dict[str, str]:
    errors: Dict[str, str] = {}

    if not email:
        errors["email"] = "Email is required."
    elif email != email.strip():
        errors["email"] = "Email must not contain leading or trailing whitespace."
    elif not EMAIL_PATTERN.match(email):
        errors["email"] = "Email format is invalid."

    if not password:
        errors["password"] = "Password is required."
    elif not password_meets_policy(password):
        errors["password"] = "Password must be at least 8 characters and include at least one letter and one number."

    return errors


def email_exists(email: str, db_path: Optional[Union[str, Path]] = None) -> bool:
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT 1 FROM user_accounts WHERE email = ? LIMIT 1",
            (email,),
        ).fetchone()
    return row is not None


def create_user_account(email: str, password: str, db_path: Optional[Union[str, Path]] = None) -> int:
    timestamp = datetime.now(timezone.utc).isoformat()
    password_hash = generate_password_hash(password)

    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO user_accounts (email, password_hash, is_active, created_at, updated_at)
            VALUES (?, ?, 1, ?, ?)
            """,
            (email, password_hash, timestamp, timestamp),
        )
    return int(cursor.lastrowid)


def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def register_user(
    *,
    email: str,
    password: str,
    session_key: str,
    submission_token: str,
    db_path: Optional[Union[str, Path]] = None,
) -> RegistrationResult:
    if not submission_token:
        return RegistrationResult(
            success=False,
            code="validation_error",
            errors={"form": "Submission token is missing. Please refresh and try again."},
        )

    if not acquire_submission_lock(session_key, submission_token):
        return RegistrationResult(
            success=False,
            code="duplicate_submission",
            errors={"form": "A registration request is already in progress. Please wait and try again."},
        )

    try:
        errors = validate_registration_input(email=email, password=password)
        if errors:
            return RegistrationResult(success=False, code="validation_error", errors=errors)

        if email_exists(email=email, db_path=db_path):
            return RegistrationResult(
                success=False,
                code="duplicate_email",
                errors={"email": "This email is already registered. Try signing in or use a different email."},
            )

        user_id = create_user_account(email=email, password=password, db_path=db_path)
        return RegistrationResult(success=True, code="success", user_id=user_id)
    finally:
        release_submission_lock(session_key, submission_token)
