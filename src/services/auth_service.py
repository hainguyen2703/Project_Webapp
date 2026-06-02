from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

from werkzeug.security import check_password_hash

from src.services.db import get_user_by_email

FAILED_LOGIN_MAX_ATTEMPTS = 3
FAILED_LOGIN_WINDOW_SECONDS = 30
THROTTLE_SECONDS = 30
SESSION_TTL_SECONDS = 1800

FAILED_LOGIN_ATTEMPTS: Dict[str, List[float]] = {}
THROTTLE_UNTIL: Dict[str, float] = {}


@dataclass
class AuthResult:
    success: bool
    code: str
    user_id: Optional[int] = None
    email: str = ""
    session_version: int = 0
    errors: Dict[str, str] = field(default_factory=dict)


def _now() -> float:
    return time.time()


def reset_auth_tracking() -> None:
    FAILED_LOGIN_ATTEMPTS.clear()
    THROTTLE_UNTIL.clear()


def _prune_attempts(identity: str, now_ts: float) -> None:
    attempts = FAILED_LOGIN_ATTEMPTS.get(identity, [])
    FAILED_LOGIN_ATTEMPTS[identity] = [ts for ts in attempts if now_ts - ts <= FAILED_LOGIN_WINDOW_SECONDS]


def is_throttled(identity: str) -> bool:
    now_ts = _now()
    until = THROTTLE_UNTIL.get(identity, 0)
    if until <= now_ts:
        THROTTLE_UNTIL.pop(identity, None)
        return False
    return True


def register_failed_attempt(identity: str) -> None:
    now_ts = _now()
    _prune_attempts(identity, now_ts)
    attempts = FAILED_LOGIN_ATTEMPTS.setdefault(identity, [])
    attempts.append(now_ts)
    if len(attempts) >= FAILED_LOGIN_MAX_ATTEMPTS:
        THROTTLE_UNTIL[identity] = now_ts + THROTTLE_SECONDS


def clear_attempt_state(identity: str) -> None:
    FAILED_LOGIN_ATTEMPTS.pop(identity, None)
    THROTTLE_UNTIL.pop(identity, None)


def authenticate_user(
    *,
    email: str,
    password: str,
    db_path: Optional[Union[str, Path]] = None,
) -> AuthResult:
    if not email:
        return AuthResult(success=False, code="validation_error", errors={"email": "Email is required."})

    if not password:
        return AuthResult(success=False, code="validation_error", errors={"password": "Password is required."})

    identity = email.strip()
    if not identity:
        return AuthResult(success=False, code="validation_error", errors={"email": "Email is required."})
    if is_throttled(identity):
        return AuthResult(
            success=False,
            code="throttled",
            errors={"form": "Too many failed attempts. Please wait and try again."},
        )

    user_row = get_user_by_email(email=identity, db_path=db_path)
    if user_row is None:
        register_failed_attempt(identity)
        return AuthResult(
            success=False,
            code="invalid_credentials",
            errors={"form": "Invalid email or password."},
        )

    if not check_password_hash(user_row["password_hash"], password):
        register_failed_attempt(identity)
        return AuthResult(
            success=False,
            code="invalid_credentials",
            errors={"form": "Invalid email or password."},
        )

    clear_attempt_state(identity)
    return AuthResult(
        success=True,
        code="success",
        user_id=int(user_row["id"]),
        email=str(user_row["email"]),
        session_version=int(user_row["session_version"]),
    )


def issue_session_expiry() -> int:
    return int(_now() + SESSION_TTL_SECONDS)


def session_is_expired(expires_at: Optional[int]) -> bool:
    if not expires_at:
        return False
    return _now() >= int(expires_at)
