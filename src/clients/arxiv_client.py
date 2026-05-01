from __future__ import annotations

import datetime
import xml.etree.ElementTree as ET
from typing import List, Optional

import requests

from src.models.article import PaperArticle


ARXIV_API_URL = "https://export.arxiv.org/api/query"


def _parse_iso(timestamp: str) -> str:
    try:
        parsed = datetime.datetime.fromisoformat(timestamp)
        return parsed.replace(tzinfo=datetime.timezone.utc).isoformat()
    except ValueError:
        return timestamp


def fetch_arxiv_articles(limit: int = 10, query: Optional[str] = None) -> List[PaperArticle]:
    search_term = query or "cat:cs.AI"
    params = {
        "search_query": f"all:{search_term}" if query else "cat:cs.AI",
        "start": 0,
        "max_results": limit,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    response = requests.get(ARXIV_API_URL, params=params, timeout=10)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    entries = root.findall("{http://www.w3.org/2005/Atom}entry")
    results: List[PaperArticle] = []

    for entry in entries:
        entry_id = entry.findtext("{http://www.w3.org/2005/Atom}id", "")
        title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "Untitled").strip()
        authors = [author.findtext("{http://www.w3.org/2005/Atom}name", "").strip() for author in entry.findall("{http://www.w3.org/2005/Atom}author") if author.find("{http://www.w3.org/2005/Atom}name") is not None]
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

    return results
