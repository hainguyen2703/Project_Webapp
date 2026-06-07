from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "app.db"


def get_connection(db_path: Optional[Union[str, Path]] = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
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

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS favourite_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                source TEXT NOT NULL,
                external_paper_id TEXT NOT NULL,
                title TEXT NOT NULL,
                authors_json TEXT NOT NULL,
                summary TEXT NOT NULL,
                url TEXT NOT NULL,
                published_at TEXT NOT NULL,
                source_label TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES user_accounts(id) ON DELETE CASCADE
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_favourites_owner_paper
            ON favourite_items(user_id, source, external_paper_id)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_favourites_owner_created
            ON favourite_items(user_id, created_at DESC)
            """
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


def favourite_exists(
    *,
    user_id: int,
    source: str,
    external_paper_id: str,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM favourite_items
            WHERE user_id = ? AND source = ? AND external_paper_id = ?
            LIMIT 1
            """,
            (user_id, source, external_paper_id),
        ).fetchone()
    return row is not None


def add_favourite(
    *,
    user_id: int,
    source: str,
    external_paper_id: str,
    paper: dict[str, Any],
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    timestamp = datetime.now(timezone.utc).isoformat()
    payload = (
        user_id,
        source,
        external_paper_id,
        str(paper.get("title", "")).strip(),
        json.dumps(paper.get("authors", [])),
        str(paper.get("summary", "")).strip(),
        str(paper.get("url", "")).strip(),
        str(paper.get("published_at", "")).strip(),
        str(paper.get("source_label", source)),
        timestamp,
        timestamp,
    )

    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO favourite_items (
                user_id,
                source,
                external_paper_id,
                title,
                authors_json,
                summary,
                url,
                published_at,
                source_label,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            payload,
        )
    return cursor.rowcount > 0


def remove_favourite(
    *,
    user_id: int,
    source: str,
    external_paper_id: str,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            DELETE FROM favourite_items
            WHERE user_id = ? AND source = ? AND external_paper_id = ?
            """,
            (user_id, source, external_paper_id),
        )
    return cursor.rowcount > 0


def get_favourite(
    *,
    user_id: int,
    source: str,
    external_paper_id: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[dict[str, Any]]:
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT source, external_paper_id, title, authors_json, summary, url, published_at, source_label, created_at
            FROM favourite_items
            WHERE user_id = ? AND source = ? AND external_paper_id = ?
            LIMIT 1
            """,
            (user_id, source, external_paper_id),
        ).fetchone()

    if row is None:
        return None

    return {
        "id": row["external_paper_id"],
        "source": row["source"],
        "title": row["title"],
        "authors": json.loads(row["authors_json"]),
        "summary": row["summary"],
        "url": row["url"],
        "published_at": row["published_at"],
        "source_label": row["source_label"],
        "created_at": row["created_at"],
    }


def list_favourites(
    *,
    user_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT source, external_paper_id, title, authors_json, summary, url, published_at, source_label, created_at
            FROM favourite_items
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()

    favourites: list[dict[str, Any]] = []
    for row in rows:
        favourites.append(
            {
                "id": row["external_paper_id"],
                "source": row["source"],
                "title": row["title"],
                "authors": json.loads(row["authors_json"]),
                "summary": row["summary"],
                "url": row["url"],
                "published_at": row["published_at"],
                "source_label": row["source_label"],
                "created_at": row["created_at"],
            }
        )
    return favourites


def delete_favourites_for_user(
    *,
    user_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "DELETE FROM favourite_items WHERE user_id = ?",
            (user_id,),
        )
    return cursor.rowcount


def delete_user_account(
    *,
    user_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "DELETE FROM user_accounts WHERE id = ?",
            (user_id,),
        )
    return cursor.rowcount > 0
