from __future__ import annotations

from flask_login import UserMixin


class AuthUser(UserMixin):
    def __init__(self, user_id: int, email: str, session_version: int) -> None:
        self.id = str(user_id)
        self.email = email
        self.session_version = session_version
