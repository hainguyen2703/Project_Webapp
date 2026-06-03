from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse


ARXIV_ID_PATTERN = re.compile(r"^(\d{4}\.\d{4,5}(?:v\d+)?|[a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)$", re.IGNORECASE)


@dataclass
class PaperArticle:
    id: str
    source: str
    title: str
    authors: List[str]
    summary: str
    url: str
    published_at: str
    source_label: str
    fetched_at: str
    thumbnail_url: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "authors": self.authors,
            "summary": self.summary,
            "url": self.url,
            "published_at": self.published_at,
            "source_label": self.source_label,
            "fetched_at": self.fetched_at,
            "thumbnail_url": self.thumbnail_url,
            "metadata": self.metadata,
        }

    @classmethod
    def validate(cls, article: PaperArticle) -> bool:
        if not article.id or not article.source or not article.title.strip():
            return False
        if not article.summary.strip() or not article.authors:
            return False
        if not ARXIV_ID_PATTERN.match(article.id):
            return False
        if not urlparse(article.url).scheme or not urlparse(article.url).netloc:
            return False
        if article.source.lower() == "arxiv" and not article.url.startswith(f"https://arxiv.org/abs/{article.id}"):
            return False
        try:
            datetime.fromisoformat(article.published_at.replace("Z", "+00:00"))
            datetime.fromisoformat(article.fetched_at.replace("Z", "+00:00"))
        except ValueError:
            return False
        return True
