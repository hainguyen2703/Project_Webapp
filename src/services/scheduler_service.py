from __future__ import annotations

import logging
from typing import Optional
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from apscheduler.schedulers.background import BackgroundScheduler

from src.services.db import (
    get_user_by_id,
    list_user_interest_keys,
    list_paper_snapshots,
    add_paper_notification,
    get_user_metadata,
    upsert_user_metadata
)
from src.services.discovery_service import ListingContextKeys, fetch_items

logger = logging.getLogger(__name__)


def check_new_papers_for_all_users():
    logger.info("Checking for new papers for all users...")
    # First, let's add a manual test notification for the current user (if any)
    # Get all users in our existing DB
    db_path = Path(__file__).resolve().parents[1] / "data" / "app.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM user_accounts WHERE is_active = 1")
    user_rows = cursor.fetchall()
    conn.close()

    for user_row in user_rows:
        user_id = user_row["id"]
        logger.info(f"Checking papers for user {user_id}")
        # Get user interests
        user_interests = list_user_interest_keys(user_id=user_id, db_path=str(db_path))
        if not user_interests:
            continue
        # Get last check time
        user_meta = get_user_metadata(user_id=user_id, db_path=str(db_path))
        last_check = user_meta["last_notification_check_at"] if user_meta else None
        if not last_check:
            # First check, set last check to now
            upsert_user_metadata(
                user_id=user_id,
                last_notification_check_at=datetime.now(timezone.utc).isoformat(),
                db_path=str(db_path)
            )
            continue
        # Get new snapshots since last check that match interests
        new_papers = []
        for interest in user_interests:
            snaps = list_paper_snapshots(category=interest, since=last_check, limit=10, db_path=str(db_path))
            new_papers.extend(snaps)
        # Deduplicate papers
        seen_ids = set()
        unique_papers = []
        for p in new_papers:
            if p["id"] not in seen_ids:
                seen_ids.add(p["id"])
                unique_papers.append(p)
        # Add notifications for each unique paper
        for paper in unique_papers:
            add_paper_notification(
                user_id=user_id,
                paper_id=paper["id"],
                paper_title=paper["title"],
                paper_url=paper["url"],
                db_path=str(db_path)
            )
            logger.info(f"Added notification for user {user_id} about paper {paper['id']}")
        # Update last check time
        upsert_user_metadata(
            user_id=user_id,
            last_notification_check_at=datetime.now(timezone.utc).isoformat(),
            db_path=str(db_path)
        )
    logger.info("New paper check complete")


class SchedulerService:
    _instance: Optional["SchedulerService"] = None
    _scheduler: Optional[BackgroundScheduler] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls):
        if cls._initialized:
            logger.warning("SchedulerService already initialized")
            return

        cls._scheduler = BackgroundScheduler()
        cls._scheduler.start()
        logger.info("APScheduler started successfully")
        cls._initialized = True

        # Add periodic job to check for new papers every 10 minutes (for testing, can change to hours later)
        cls._scheduler.add_job(
            func=check_new_papers_for_all_users,
            trigger="interval",
            minutes=5,
            id="check_new_papers",
            replace_existing=True,
            next_run_time=datetime.now()
        )
        logger.info("Scheduled new paper check job")

    @classmethod
    def shutdown(cls):
        if cls._scheduler and cls._scheduler.running:
            cls._scheduler.shutdown(wait=True)
            logger.info("APScheduler shutdown")
            cls._initialized = False

    @classmethod
    def is_running(cls) -> bool:
        return cls._initialized and cls._scheduler and cls._scheduler.running

    @classmethod
    def get_scheduler(cls) -> Optional[BackgroundScheduler]:
        return cls._scheduler
