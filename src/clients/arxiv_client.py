from __future__ import annotations

import time
import datetime
import xml.etree.ElementTree as ET
from typing import List, Optional

import requests

from src.models.article import PaperArticle


ARXIV_API_URL = "https://export.arxiv.org/api/query"

# Cache để tránh gọi API liên tục
CACHE = {}
LAST_FETCH_TIME = 0

# User-Agent chuẩn để tránh bị arXiv chặn
HEADERS = {
    "User-Agent": "HariResearchBot/1.0 (mailto:nguyenngochai27031995@gmail.com)"
}


def _parse_iso(timestamp: str) -> str:
    try:
        parsed = datetime.datetime.fromisoformat(timestamp)
        return parsed.replace(tzinfo=datetime.timezone.utc).isoformat()
    except ValueError:
        return timestamp


def fetch_arxiv_articles(limit: int = 10, query: Optional[str] = None) -> List[PaperArticle]:
    global LAST_FETCH_TIME

    search_term = query or "cat:cs.AI"
    cache_key = f"{search_term}:{limit}"

    # 1) Nếu đã có trong cache → trả về ngay
    if cache_key in CACHE:
        return CACHE[cache_key]

    # 2) Không cho phép gọi API quá 1 lần mỗi 10 giây
    now = time.time()
    if now - LAST_FETCH_TIME < 10:
        return CACHE.get(cache_key, [])

    LAST_FETCH_TIME = now

    params = {
        "search_query": f"all:{search_term}" if query else "cat:cs.AI",
        "start": 0,
        "max_results": limit,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    # 3) Retry tối đa 3 lần (đủ để tránh bị chặn mà không spam)
    for attempt in range(3):
        try:
            response = requests.get(
                ARXIV_API_URL,
                params=params,
                timeout=30,          # timeout lớn để tránh lỗi read timed out
                headers=HEADERS
            )

            # Nếu bị rate-limit → đợi 6 giây rồi thử lại
            if response.status_code == 429:
                time.sleep(6)
                continue

            response.raise_for_status()
            break

        except requests.exceptions.ReadTimeout:
            # Nếu timeout → đợi 6 giây rồi thử lại
            time.sleep(6)
            continue

    else:
        # Nếu retry 3 lần vẫn fail → trả cache (nếu có) hoặc list rỗng
        if cache_key in CACHE:
            return CACHE[cache_key]
        return []

    # 4) Parse XML như code gốc của bạn
    root = ET.fromstring(response.text)
    entries = root.findall("{http://www.w3.org/2005/Atom}entry")
    results: List[PaperArticle] = []

    for entry in entries:
        entry_id = entry.findtext("{http://www.w3.org/2005/Atom}id", "")
        title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "Untitled").strip()
        authors = [
            author.findtext("{http://www.w3.org/2005/Atom}name", "").strip()
            for author in entry.findall("{http://www.w3.org/2005/Atom}author")
            if author.find("{http://www.w3.org/2005/Atom}name") is not None
        ]
        summary = (entry.findtext("{http://www.w3.org/2005/Atom}summary") or "No summary available.").strip()
        url = entry_id
        published = entry.findtext("{http://www.w3.org/2005/Atom}published") or datetime.datetime.now(datetime.timezone.utc).isoformat()
        fetched_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        primary_category = entry.find("{http://arxiv.org/schemas/atom}primary_category")

        article = PaperArticle(
            id=entry_id,
            source="arxiv",
            title=title,
            authors=authors,
            summary=summary,
            url=url,
            published_at=_parse_iso(published),
            source_label="arXiv",
            fetched_at=fetched_at,
            metadata={"primary_category": primary_category.get("term") if primary_category is not None else ""},
        )
        results.append(article)

    # 5) Lưu vào cache
    CACHE[cache_key] = results

    return results
