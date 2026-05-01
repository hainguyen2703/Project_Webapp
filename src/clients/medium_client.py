from __future__ import annotations

import datetime
import xml.etree.ElementTree as ET
from typing import List, Optional

import requests

from src.models.article import PaperArticle


MEDIUM_FEED_URL = "https://medium.com/feed/tag/technology"


def _parse_iso(timestamp: Optional[str]) -> str:
    if not timestamp:
        return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    try:
        parsed = datetime.datetime.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %Z")
        return parsed.replace(tzinfo=datetime.timezone.utc).isoformat()
    except ValueError:
        try:
            parsed = datetime.datetime.fromisoformat(timestamp)
            return parsed.replace(tzinfo=datetime.timezone.utc).isoformat()
        except ValueError:
            return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()


def fetch_medium_articles(limit: int = 10, query: Optional[str] = None) -> List[PaperArticle]:
    feed_url = MEDIUM_FEED_URL
    response = requests.get(feed_url, timeout=10)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    items = root.findall(".//item")[:limit]
    results: List[PaperArticle] = []

    for item in items:
        guid = item.findtext("guid", "") or item.findtext("link", "")
        title = (item.findtext("title") or "Untitled").strip()
        author = item.findtext("{http://purl.org/dc/elements/1.1/}creator")
        authors = [author.strip()] if author else ["Unknown"]
        summary = (item.findtext("description") or "No summary available.").strip()
        url = (item.findtext("link") or guid).strip()
        published = item.findtext("pubDate")
        fetched_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        article = PaperArticle(
            id=guid,
            source="medium",
            title=title,
            authors=authors,
            summary=summary,
            url=url,
            published_at=_parse_iso(published),
            source_label="Medium",
            fetched_at=fetched_at,
            metadata={"creator": authors[0] if authors else "Unknown"},
        )
        results.append(article)

    return results
