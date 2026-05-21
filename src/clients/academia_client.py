from __future__ import annotations

import datetime
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from src.models.article import PaperArticle


ACADEMIA_SEARCH_URL = "https://www.academia.edu/search"
DEFAULT_QUERY = "computer science"
_BASE_URL = "https://www.academia.edu"


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _extract_text(element, *selectors: str, default: str = "") -> str:
    """Try each CSS selector in order; return stripped text of first match."""
    for selector in selectors:
        tag = element.select_one(selector)
        if tag and tag.get_text(strip=True):
            return tag.get_text(strip=True)
    return default


def fetch_academia_articles(limit: int = 10, query: Optional[str] = None) -> List[PaperArticle]:
    search_query = query or DEFAULT_QUERY
    response = requests.get(
        ACADEMIA_SEARCH_URL,
        params={"q": search_query},
        headers={"User-Agent": "PaperDiscovery/1.0"},
        timeout=10,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    containers = soup.find_all("div", attrs={"data-document-id": True})[:limit]
    results: List[PaperArticle] = []
    fetched_at = _now_iso()

    for container in containers:
        doc_id = container.get("data-document-id", "")

        # Title + URL
        title_tag = container.select_one("a.document-title") or container.select_one("h3 > a")
        title = title_tag.get_text(strip=True) if title_tag else "Untitled"
        raw_href = title_tag.get("href", "") if title_tag else ""
        if raw_href.startswith("http"):
            url = raw_href
        elif raw_href:
            url = _BASE_URL + raw_href
        else:
            url = f"{_BASE_URL}/{doc_id}/" if doc_id else _BASE_URL

        # Authors
        author_text = _extract_text(container, "span.author-name", default="")
        authors = [author_text] if author_text else ["Unknown"]

        # Summary / snippet
        summary = _extract_text(
            container,
            "p.preview",
            "div.document-summary",
            default="No summary available.",
        )

        # Date — prefer <time datetime="..."> attr, then span text, then now
        time_tag = container.find("time")
        if time_tag and time_tag.get("datetime"):
            published_at = time_tag["datetime"]
            # Normalise to ISO format if it's just a year or date string
            try:
                dt = datetime.datetime.fromisoformat(published_at)
                published_at = dt.replace(tzinfo=datetime.timezone.utc).isoformat()
            except ValueError:
                # e.g. "2025" — wrap as Jan 1
                try:
                    published_at = datetime.datetime(int(published_at), 1, 1,
                                                     tzinfo=datetime.timezone.utc).isoformat()
                except (ValueError, TypeError):
                    published_at = fetched_at
        else:
            date_text = _extract_text(container, "span.document-date", default="")
            published_at = date_text if date_text else fetched_at

        article = PaperArticle(
            id=url,
            source="academia",
            title=title,
            authors=authors,
            summary=summary,
            url=url,
            published_at=published_at,
            source_label="Academia.edu",
            fetched_at=fetched_at,
            metadata={"doc_id": doc_id},
        )
        results.append(article)

    return results
