from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional, Union

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "app.db"


def get_connection(db_path: Optional[Union[str, Path]] = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: Optional[Union[str, Path]] = None) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                session_version INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_user_accounts_email
            ON user_accounts(email)
            """
        )

        # Backfill for databases created before session_version was introduced.
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(user_accounts)").fetchall()
        }
        if "session_version" not in columns:
            connection.execute(
                "ALTER TABLE user_accounts ADD COLUMN session_version INTEGER NOT NULL DEFAULT 0"
            )


def get_user_by_email(
    *,
    email: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[sqlite3.Row]:
    with get_connection(db_path) as connection:
        return connection.execute(
            "SELECT * FROM user_accounts WHERE email = ? LIMIT 1",
            (email,),
        ).fetchone()


def get_user_by_id(
    *,
    user_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[sqlite3.Row]:
    with get_connection(db_path) as connection:
        return connection.execute(
            "SELECT * FROM user_accounts WHERE id = ? LIMIT 1",
            (user_id,),
        ).fetchone()


def bump_session_version(
    *,
    user_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> int:
    with get_connection(db_path) as connection:
        connection.execute(
            "UPDATE user_accounts SET session_version = session_version + 1 WHERE id = ?",
            (user_id,),
        )
        row = connection.execute(
            "SELECT session_version FROM user_accounts WHERE id = ?",
            (user_id,),
        ).fetchone()

    if row is None:
        return 0
    return int(row["session_version"])
