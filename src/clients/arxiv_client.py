from __future__ import annotations

import datetime
import re
import time
from typing import List, Optional

import arxiv

from src.models.article import PaperArticle

DEFAULT_QUERY = "cat:cs.AI"
REQUEST_TIMEOUT_SECONDS = 30
CACHE: dict[str, List[PaperArticle]] = {}

_ARXIV_ID_PATTERNS = [
    re.compile(r"(\d{4}\.\d{4,5}(?:v\d+)?)$"),
    re.compile(r"([a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)$", re.IGNORECASE),
]


def _parse_iso(timestamp: object) -> str:
    if isinstance(timestamp, datetime.datetime):
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
        return timestamp.astimezone(datetime.timezone.utc).isoformat()

    if not isinstance(timestamp, str):
        return datetime.datetime.now(datetime.timezone.utc).isoformat()

    try:
        parsed = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=datetime.timezone.utc)
        return parsed.replace(tzinfo=datetime.timezone.utc).isoformat()
    except ValueError:
        return datetime.datetime.now(datetime.timezone.utc).isoformat()


def extract_arxiv_id(raw_id: str) -> Optional[str]:
    if not raw_id:
        return None

    cleaned = raw_id.strip()
    cleaned = cleaned.split("?")[0].rstrip("/")

    for pattern in _ARXIV_ID_PATTERNS:
        match = pattern.search(cleaned)
        if match:
            return match.group(1)

    return None


def _build_canonical_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/abs/{arxiv_id}"


def _build_query(query: Optional[str]) -> str:
    if not query:
        return DEFAULT_QUERY

    normalized = query.strip()
    if not normalized:
        return DEFAULT_QUERY

    # Nếu query đã có field prefix (cat:, ti:, au:, etc.) → giữ nguyên
    if ":" in normalized:
        return normalized

    # Nếu chỉ là text search → thêm all:
    return f"all:{normalized}"



def fetch_arxiv_articles(limit: int = 10, query: Optional[str] = None, timeout_seconds: int = REQUEST_TIMEOUT_SECONDS) -> List[PaperArticle]:
    if arxiv is None:
        raise RuntimeError("Python package 'arxiv' is required for discovery retrieval.")

    search_query = _build_query(query)
    cache_key = f"{search_query}:{limit}"

    if cache_key in CACHE:
        return CACHE[cache_key]

    search = arxiv.Search(
        query=search_query,
        max_results=limit,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    client = arxiv.Client(page_size=min(limit, 100), delay_seconds=3.0, num_retries=5)
    deadline = time.monotonic() + timeout_seconds
    results: List[PaperArticle] = []

    for result in client.results(search):
        if time.monotonic() > deadline:
            raise TimeoutError("arXiv retrieval timed out.")

        raw_id = getattr(result, "entry_id", "")
        fallback_id = ""
        get_short_id = getattr(result, "get_short_id", None)
        if callable(get_short_id):
            fallback_id = str(get_short_id())

        arxiv_id = extract_arxiv_id(raw_id) or extract_arxiv_id(fallback_id) or ""
        title = str(getattr(result, "title", "") or "").strip()
        summary = str(getattr(result, "summary", "") or "").strip()
        raw_authors = getattr(result, "authors", []) or []
        authors = [str(getattr(author, "name", "") or "").strip() for author in raw_authors if str(getattr(author, "name", "") or "").strip()]
        published = _parse_iso(getattr(result, "published", ""))
        fetched_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        primary_category = str(getattr(result, "primary_category", "") or "").lower()
        canonical_url = _build_canonical_url(arxiv_id) if arxiv_id else str(raw_id or "")

        article = PaperArticle(
            id=arxiv_id,
            source="arxiv",
            title=title,
            authors=authors,
            summary=summary,
            url=canonical_url,
            published_at=published,
            source_label="arXiv",
            fetched_at=fetched_at,
            metadata={"primary_category": primary_category},
        )
        results.append(article)

    CACHE[cache_key] = results
    return results
