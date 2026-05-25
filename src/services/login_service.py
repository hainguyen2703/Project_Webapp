from __future__ import annotations

from typing import Optional, Tuple

from werkzeug.security import check_password_hash

from src.models.user import UserAccount

_INVALID_MSG = "Invalid email or password."


def login_user(email: str, password: str) -> Tuple[Optional[int], Optional[str]]:
    """Verify credentials and return (user_id, None) on success or (None, error) on failure."""
    user = UserAccount.query.filter_by(email=email.strip().lower()).first()

    if user is None or user.status != "active" or not check_password_hash(user.password_hash, password):
        return None, _INVALID_MSG

    return user.id, None
