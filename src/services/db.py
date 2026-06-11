from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "app.db"

INTEREST_CATALOG: list[dict[str, Any]] = [
    {"key": "cs.ai", "label": "Artificial Intelligence", "is_default": 1, "sort_order": 10},
    {"key": "cs.cl", "label": "Computation and Language", "is_default": 1, "sort_order": 20},
    {"key": "cs.cv", "label": "Computer Vision and Pattern Recognition", "is_default": 1, "sort_order": 30},
    {"key": "cs.lg", "label": "Machine Learning", "is_default": 1, "sort_order": 40},
    {"key": "cs.ds", "label": "Data Structures and Algorithms", "is_default": 0, "sort_order": 50},
    {"key": "cs.ro", "label": "Robotics", "is_default": 0, "sort_order": 60},
    {"key": "cs.se", "label": "Software Engineering", "is_default": 0, "sort_order": 70},
    {"key": "cs.db", "label": "Databases", "is_default": 0, "sort_order": 80},
    {"key": "cs.dc", "label": "Distributed, Parallel, and Cluster Computing", "is_default": 0, "sort_order": 90},
    {"key": "cs.cy", "label": "Computers and Society", "is_default": 0, "sort_order": 100},
    {"key": "cs.cr", "label": "Cryptography and Security", "is_default": 0, "sort_order": 110},
    {"key": "cs.lo", "label": "Logic in Computer Science", "is_default": 0, "sort_order": 120},
    {"key": "cs.ma", "label": "Multiagent Systems", "is_default": 0, "sort_order": 130},
    {"key": "cs.ne", "label": "Neural and Evolutionary Computing", "is_default": 0, "sort_order": 140},
    {"key": "cs.ni", "label": "Networking and Internet Architecture", "is_default": 0, "sort_order": 150},
    {"key": "cs.os", "label": "Operating Systems", "is_default": 0, "sort_order": 160},
    {"key": "cs.pl", "label": "Programming Languages", "is_default": 0, "sort_order": 170},
    {"key": "cs.sd", "label": "Sound", "is_default": 0, "sort_order": 180},
    {"key": "cs.si", "label": "Social and Information Networks", "is_default": 0, "sort_order": 190},
    {"key": "cs.sy", "label": "Systems and Control", "is_default": 0, "sort_order": 200},
    {"key": "cs.ce", "label": "Computational Engineering, Finance, and Science", "is_default": 0, "sort_order": 210},
    {"key": "cs.cg", "label": "Computational Geometry", "is_default": 0, "sort_order": 220},
    {"key": "cs.gt", "label": "Computer Science and Game Theory", "is_default": 0, "sort_order": 230},
    {"key": "cs.dg", "label": "Digital Libraries", "is_default": 0, "sort_order": 240},
    {"key": "cs.dm", "label": "Discrete Mathematics", "is_default": 0, "sort_order": 250},
    {"key": "cs.gl", "label": "General Literature", "is_default": 0, "sort_order": 260},
    {"key": "cs.gr", "label": "Graphics", "is_default": 0, "sort_order": 270},
    {"key": "cs.ar", "label": "Hardware Architecture", "is_default": 0, "sort_order": 280},
    {"key": "cs.hc", "label": "Human-Computer Interaction", "is_default": 0, "sort_order": 290},
    {"key": "cs.ir", "label": "Information Retrieval", "is_default": 0, "sort_order": 300},
    {"key": "cs.it", "label": "Information Theory", "is_default": 0, "sort_order": 310},
    {"key": "cs.mm", "label": "Multimedia", "is_default": 0, "sort_order": 320},
    {"key": "cs.na", "label": "Numerical Analysis", "is_default": 0, "sort_order": 330},
    {"key": "cs.ms", "label": "Mathematical Software", "is_default": 0, "sort_order": 340},
    {"key": "cs.pf", "label": "Performance", "is_default": 0, "sort_order": 350},
    {"key": "cs.sc", "label": "Symbolic Computation", "is_default": 0, "sort_order": 360},
]




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

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS interest_topics (
                key TEXT PRIMARY KEY,
                label TEXT NOT NULL UNIQUE,
                is_active INTEGER NOT NULL DEFAULT 1,
                is_default INTEGER NOT NULL DEFAULT 0,
                sort_order INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_interest_preferences (
                user_id INTEGER PRIMARY KEY,
                onboarding_completed INTEGER NOT NULL DEFAULT 0,
                last_updated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES user_accounts(id) ON DELETE CASCADE
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_interest_selections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                interest_key TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES user_accounts(id) ON DELETE CASCADE,
                FOREIGN KEY(interest_key) REFERENCES interest_topics(key)
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_user_interest_owner_key
            ON user_interest_selections(user_id, interest_key)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_user_interest_owner
            ON user_interest_selections(user_id)
            """
        )

        # New advanced features tables
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS paper_snapshots (
                id TEXT NOT NULL,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                authors_json TEXT NOT NULL,
                summary TEXT NOT NULL,
                url TEXT NOT NULL,
                published_at TEXT NOT NULL,
                primary_category TEXT,
                categories_json TEXT,
                snapshot_at TEXT NOT NULL,
                metadata_json TEXT,
                PRIMARY KEY (id, source)
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_paper_snapshots_published_at
            ON paper_snapshots(published_at DESC)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_paper_snapshots_primary_category
            ON paper_snapshots(primary_category)
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS paper_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id TEXT NOT NULL,
                user_id INTEGER,
                overall_score REAL NOT NULL,
                recency_score REAL NOT NULL,
                relevance_score REAL NOT NULL,
                popularity_score REAL NOT NULL,
                calculated_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES user_accounts(id) ON DELETE CASCADE
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_paper_scores_paper_user
            ON paper_scores(paper_id, user_id)
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS paper_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_paper_id TEXT NOT NULL,
                target_paper_id TEXT NOT NULL,
                similarity_score REAL NOT NULL,
                similarity_type TEXT NOT NULL,
                calculated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_paper_relations_source_target
            ON paper_relations(source_paper_id, target_paper_id, similarity_type)
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS paper_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                paper_id TEXT NOT NULL,
                paper_title TEXT NOT NULL,
                paper_url TEXT NOT NULL,
                notification_type TEXT NOT NULL DEFAULT 'new_paper',
                is_read INTEGER NOT NULL DEFAULT 0,
                is_dismissed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                delivered_at TEXT,
                FOREIGN KEY(user_id) REFERENCES user_accounts(id) ON DELETE CASCADE
            )
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_paper_notifications_user
            ON paper_notifications(user_id, is_dismissed, created_at DESC)
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS category_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                date_bucket TEXT NOT NULL,
                paper_count INTEGER NOT NULL DEFAULT 0,
                top_authors_json TEXT,
                hot_keywords_json TEXT,
                calculated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS ux_category_stats_category_date
            ON category_stats(category, date_bucket)
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS user_metadata (
                user_id INTEGER PRIMARY KEY,
                last_login_at TEXT NOT NULL,
                last_notification_check_at TEXT,
                FOREIGN KEY(user_id) REFERENCES user_accounts(id) ON DELETE CASCADE
            )
            """
        )

        _seed_interest_catalog(connection)


def _seed_interest_catalog(connection: sqlite3.Connection) -> None:
    now = datetime.now(timezone.utc).isoformat()
    for topic in INTEREST_CATALOG:
        connection.execute(
            """
            INSERT INTO interest_topics (key, label, is_active, is_default, sort_order, updated_at)
            VALUES (?, ?, 1, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                label = excluded.label,
                is_default = excluded.is_default,
                sort_order = excluded.sort_order,
                updated_at = excluded.updated_at
            """,
            (
                topic["key"],
                topic["label"],
                int(topic["is_default"]),
                int(topic["sort_order"]),
                now,
            ),
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


def get_interest_label(key: str) -> str:
    key = key.lower()
    for item in INTEREST_CATALOG:
        if item["key"] == key:
            return item["label"]
    return key  # fallback


def list_interest_topics(
    *,
    active_only: bool = True,
    db_path: Optional[Union[str, Path]] = None,
) -> list[dict[str, Any]]:
    query = """
        SELECT key, label, is_active, is_default, sort_order
        FROM interest_topics
    """
    params: tuple[Any, ...] = ()
    if active_only:
        query += " WHERE is_active = 1"
    query += " ORDER BY sort_order ASC, label ASC"

    with get_connection(db_path) as connection:
        rows = connection.execute(query, params).fetchall()

    return [
        {
            "key": row["key"],
            "label": row["label"],
            "is_active": bool(row["is_active"]),
            "is_default": bool(row["is_default"]),
            "sort_order": int(row["sort_order"]),
        }
        for row in rows
    ]


def list_default_interest_keys(
    *,
    db_path: Optional[Union[str, Path]] = None,
) -> list[str]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT key
            FROM interest_topics
            WHERE is_active = 1 AND is_default = 1
            ORDER BY sort_order ASC, label ASC
            """
        ).fetchall()
    return [str(row["key"]) for row in rows]


def list_user_interest_keys(
    *,
    user_id: int,
    active_only: bool = True,
    db_path: Optional[Union[str, Path]] = None,
) -> list[str]:
    query = """
        SELECT s.interest_key
        FROM user_interest_selections s
        JOIN interest_topics t ON t.key = s.interest_key
        WHERE s.user_id = ?
    """
    params: list[Any] = [user_id]
    if active_only:
        query += " AND t.is_active = 1"
    query += " ORDER BY t.sort_order ASC, t.label ASC"

    with get_connection(db_path) as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
    return [str(row["interest_key"]) for row in rows]


def is_onboarding_completed(
    *,
    user_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT onboarding_completed FROM user_interest_preferences WHERE user_id = ? LIMIT 1",
            (user_id,),
        ).fetchone()
    if row is None:
        return False
    return bool(row["onboarding_completed"])


def set_user_interest_preferences(
    *,
    user_id: int,
    interest_keys: list[str],
    onboarding_completed: bool,
    db_path: Optional[Union[str, Path]] = None,
) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    deduped_keys = list(dict.fromkeys(interest_keys))

    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO user_interest_preferences (user_id, onboarding_completed, last_updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                onboarding_completed = excluded.onboarding_completed,
                last_updated_at = excluded.last_updated_at
            """,
            (user_id, int(onboarding_completed), timestamp),
        )
        connection.execute("DELETE FROM user_interest_selections WHERE user_id = ?", (user_id,))
        for key in deduped_keys:
            connection.execute(
                """
                INSERT OR IGNORE INTO user_interest_selections (user_id, interest_key, created_at)
                VALUES (?, ?, ?)
                """,
                (user_id, key, timestamp),
            )


def cleanup_retired_interests_for_user(
    *,
    user_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> int:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            DELETE FROM user_interest_selections
            WHERE user_id = ?
              AND interest_key IN (
                  SELECT key FROM interest_topics WHERE is_active = 0
              )
            """,
            (user_id,),
        )
    return cursor.rowcount


def autofill_default_interests_if_needed(
    *,
    user_id: int,
    minimum_count: int,
    db_path: Optional[Union[str, Path]] = None,
) -> list[str]:
    current = list_user_interest_keys(user_id=user_id, active_only=True, db_path=db_path)
    if len(current) >= minimum_count:
        return current

    candidate_keys: list[str] = []
    for key in list_default_interest_keys(db_path=db_path):
        if key not in candidate_keys:
            candidate_keys.append(key)
    for topic in list_interest_topics(active_only=True, db_path=db_path):
        key = str(topic["key"])
        if key not in candidate_keys:
            candidate_keys.append(key)

    for key in candidate_keys:
        if key in current:
            continue
        current.append(key)
        if len(current) >= minimum_count:
            break

    set_user_interest_preferences(
        user_id=user_id,
        interest_keys=current,
        onboarding_completed=True,
        db_path=db_path,
    )
    return list_user_interest_keys(user_id=user_id, active_only=True, db_path=db_path)


def reconcile_user_interests(
    *,
    user_id: int,
    minimum_count: int,
    db_path: Optional[Union[str, Path]] = None,
) -> list[str]:
    cleanup_retired_interests_for_user(user_id=user_id, db_path=db_path)
    if not is_onboarding_completed(user_id=user_id, db_path=db_path):
        return list_user_interest_keys(user_id=user_id, active_only=True, db_path=db_path)
    return autofill_default_interests_if_needed(
        user_id=user_id,
        minimum_count=minimum_count,
        db_path=db_path,
    )


def load_effective_interest_context(
    *,
    user_id: int,
    minimum_count: int,
    db_path: Optional[Union[str, Path]] = None,
) -> dict[str, Any]:
    before_keys = list_user_interest_keys(user_id=user_id, active_only=False, db_path=db_path)
    effective_keys = reconcile_user_interests(
        user_id=user_id,
        minimum_count=minimum_count,
        db_path=db_path,
    )
    active_keys = set(list_user_interest_keys(user_id=user_id, active_only=True, db_path=db_path))
    retired_keys = [key for key in before_keys if key not in active_keys]

    return {
        "user_id": user_id,
        "effective_interest_keys": effective_keys,
        "retired_interest_keys": retired_keys,
        "minimum_required": minimum_count,
        "last_reconciled_at": datetime.now(timezone.utc).isoformat(),
    }


# --- Advanced Features: Paper Snapshots ---

def save_paper_snapshot(
    *,
    paper_id: str,
    source: str,
    title: str,
    authors: list[str],
    summary: str,
    url: str,
    published_at: str,
    primary_category: Optional[str] = None,
    categories: Optional[list[str]] = None,
    metadata: Optional[dict[str, Any]] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    timestamp = datetime.now(timezone.utc).isoformat()
    authors_json = json.dumps(authors)
    categories_json = json.dumps(categories or [])
    metadata_json = json.dumps(metadata or {})
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT OR REPLACE INTO paper_snapshots (
                id, source, title, authors_json, summary, url, published_at, 
                primary_category, categories_json, snapshot_at, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                paper_id, source, title, authors_json, summary, url, published_at,
                primary_category, categories_json, timestamp, metadata_json
            ),
        )
    return cursor.rowcount > 0


def get_paper_snapshot(
    *,
    paper_id: str,
    source: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[dict[str, Any]]:
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT id, source, title, authors_json, summary, url, published_at, 
                   primary_category, categories_json, snapshot_at, metadata_json
            FROM paper_snapshots
            WHERE id = ? AND source = ?
            LIMIT 1
            """,
            (paper_id, source),
        ).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "source": row["source"],
        "title": row["title"],
        "authors": json.loads(row["authors_json"]),
        "summary": row["summary"],
        "url": row["url"],
        "published_at": row["published_at"],
        "primary_category": row["primary_category"],
        "categories": json.loads(row["categories_json"]),
        "snapshot_at": row["snapshot_at"],
        "metadata": json.loads(row["metadata_json"]),
    }


def list_paper_snapshots(
    *,
    category: Optional[str] = None,
    since: Optional[str] = None,
    limit: Optional[int] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> list[dict[str, Any]]:
    query = """
        SELECT id, source, title, authors_json, summary, url, published_at, 
               primary_category, categories_json, snapshot_at, metadata_json
        FROM paper_snapshots
    """
    params = []
    if category:
        query += " WHERE primary_category = ?"
        params.append(category)
    if since:
        if category:
            query += " AND published_at >= ?"
        else:
            query += " WHERE published_at >= ?"
        params.append(since)
    query += " ORDER BY published_at DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    with get_connection(db_path) as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
    return [
        {
            "id": r["id"],
            "source": r["source"],
            "title": r["title"],
            "authors": json.loads(r["authors_json"]),
            "summary": r["summary"],
            "url": r["url"],
            "published_at": r["published_at"],
            "primary_category": r["primary_category"],
            "categories": json.loads(r["categories_json"]),
            "snapshot_at": r["snapshot_at"],
            "metadata": json.loads(r["metadata_json"]),
        }
        for r in rows
    ]


# --- Advanced Features: User Metadata ---

def get_user_metadata(
    *,
    user_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[dict[str, Any]]:
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT user_id, last_login_at, last_notification_check_at FROM user_metadata WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    if not row:
        return None
    return {
        "user_id": row["user_id"],
        "last_login_at": row["last_login_at"],
        "last_notification_check_at": row["last_notification_check_at"],
    }


def upsert_user_metadata(
    *,
    user_id: int,
    last_login_at: Optional[str] = None,
    last_notification_check_at: Optional[str] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> None:
    now = datetime.now(timezone.utc).isoformat()
    existing = get_user_metadata(user_id=user_id, db_path=db_path)
    ll_at = last_login_at or (existing["last_login_at"] if existing else now)
    lnc_at = last_notification_check_at or (existing["last_notification_check_at"] if existing else None)
    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO user_metadata (user_id, last_login_at, last_notification_check_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                last_login_at = excluded.last_login_at,
                last_notification_check_at = excluded.last_notification_check_at
            """,
            (user_id, ll_at, lnc_at),
        )


# --- Advanced Features: Paper Notifications ---

def add_paper_notification(
    *,
    user_id: int,
    paper_id: str,
    paper_title: str,
    paper_url: str,
    notification_type: str = "new_paper",
    db_path: Optional[Union[str, Path]] = None,
) -> int:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO paper_notifications (
                user_id, paper_id, paper_title, paper_url, 
                notification_type, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, paper_id, paper_title, paper_url, notification_type, now),
        )
        return cursor.lastrowid or 0


def list_user_notifications(
    *,
    user_id: int,
    only_undismissed: bool = True,
    limit: Optional[int] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> list[dict[str, Any]]:
    query = """
        SELECT id, user_id, paper_id, paper_title, paper_url, notification_type,
               is_read, is_dismissed, created_at, delivered_at
        FROM paper_notifications
        WHERE user_id = ?
    """
    params = [user_id]
    if only_undismissed:
        query += " AND is_dismissed = 0"
    query += " ORDER BY created_at DESC"
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    with get_connection(db_path) as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
    return [
        {
            "id": r["id"],
            "user_id": r["user_id"],
            "paper_id": r["paper_id"],
            "paper_title": r["paper_title"],
            "paper_url": r["paper_url"],
            "notification_type": r["notification_type"],
            "is_read": bool(r["is_read"]),
            "is_dismissed": bool(r["is_dismissed"]),
            "created_at": r["created_at"],
            "delivered_at": r["delivered_at"],
        }
        for r in rows
    ]


def mark_notification_read(
    *,
    notification_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "UPDATE paper_notifications SET is_read = 1 WHERE id = ?",
            (notification_id,),
        )
    return cursor.rowcount > 0


def mark_notification_dismissed(
    *,
    notification_id: int,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            "UPDATE paper_notifications SET is_dismissed = 1 WHERE id = ?",
            (notification_id,),
        )
    return cursor.rowcount > 0


# --- Advanced Features: Paper Scores & Relations ---

def save_paper_score(
    *,
    paper_id: str,
    user_id: Optional[int],
    overall_score: float,
    recency_score: float,
    relevance_score: float,
    popularity_score: float,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT OR REPLACE INTO paper_scores (
                paper_id, user_id, overall_score, recency_score, relevance_score, popularity_score, calculated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (paper_id, user_id, overall_score, recency_score, relevance_score, popularity_score, now),
        )
    return cursor.rowcount > 0


def get_paper_score(
    *,
    paper_id: str,
    user_id: Optional[int],
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[dict[str, Any]]:
    query = """
        SELECT paper_id, user_id, overall_score, recency_score, relevance_score, popularity_score, calculated_at
        FROM paper_scores
        WHERE paper_id = ?
    """
    params = [paper_id]
    if user_id is not None:
        query += " AND user_id = ?"
        params.append(user_id)
    else:
        query += " AND user_id IS NULL"
    with get_connection(db_path) as connection:
        row = connection.execute(query, tuple(params)).fetchone()
    if not row:
        return None
    return {
        "paper_id": row["paper_id"],
        "user_id": row["user_id"],
        "overall_score": row["overall_score"],
        "recency_score": row["recency_score"],
        "relevance_score": row["relevance_score"],
        "popularity_score": row["popularity_score"],
        "calculated_at": row["calculated_at"],
    }


def save_paper_relation(
    *,
    source_paper_id: str,
    target_paper_id: str,
    similarity_score: float,
    similarity_type: str = "combined",
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT OR REPLACE INTO paper_relations (
                source_paper_id, target_paper_id, similarity_score, similarity_type, calculated_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (source_paper_id, target_paper_id, similarity_score, similarity_type, now),
        )
    return cursor.rowcount > 0


def get_related_papers(
    *,
    source_paper_id: str,
    similarity_type: str = "combined",
    limit: int = 5,
    db_path: Optional[Union[str, Path]] = None,
) -> list[dict[str, Any]]:
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT target_paper_id, similarity_score, similarity_type, calculated_at
            FROM paper_relations
            WHERE source_paper_id = ? AND similarity_type = ?
            ORDER BY similarity_score DESC
            LIMIT ?
            """,
            (source_paper_id, similarity_type, limit),
        ).fetchall()
    return [
        {
            "target_paper_id": r["target_paper_id"],
            "similarity_score": r["similarity_score"],
            "similarity_type": r["similarity_type"],
            "calculated_at": r["calculated_at"],
        }
        for r in rows
    ]


# --- Advanced Features: Category Stats ---

def save_category_stats(
    *,
    category: str,
    date_bucket: str,
    paper_count: int,
    top_authors: Optional[list[str]] = None,
    hot_keywords: Optional[list[str]] = None,
    db_path: Optional[Union[str, Path]] = None,
) -> bool:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as connection:
        cursor = connection.execute(
            """
            INSERT OR REPLACE INTO category_stats (
                category, date_bucket, paper_count, top_authors_json, hot_keywords_json, calculated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                category, date_bucket, paper_count,
                json.dumps(top_authors or []), json.dumps(hot_keywords or []), now
            ),
        )
    return cursor.rowcount > 0


def get_category_stats(
    *,
    category: str,
    date_bucket: str,
    db_path: Optional[Union[str, Path]] = None,
) -> Optional[dict[str, Any]]:
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT category, date_bucket, paper_count, top_authors_json, hot_keywords_json, calculated_at
            FROM category_stats
            WHERE category = ? AND date_bucket = ?
            LIMIT 1
            """,
            (category, date_bucket),
        ).fetchone()
    if not row:
        return None
    return {
        "category": row["category"],
        "date_bucket": row["date_bucket"],
        "paper_count": row["paper_count"],
        "top_authors": json.loads(row["top_authors_json"]),
        "hot_keywords": json.loads(row["hot_keywords_json"]),
        "calculated_at": row["calculated_at"],
    }
