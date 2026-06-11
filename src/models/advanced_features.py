from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .article import PaperArticle


class SimilarityType(Enum):
    TITLE = "title"
    SUMMARY = "summary"
    COMBINED = "combined"


class NotificationType(Enum):
    NEW_PAPER = "new_paper"


@dataclass
class PaperScore:
    paper_id: str
    user_id: Optional[int] = None
    overall_score: float = 0.0
    recency_score: float = 0.0
    relevance_score: float = 0.0
    popularity_score: float = 0.0
    calculated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, object]:
        return {
            "paper_id": self.paper_id,
            "user_id": self.user_id,
            "overall_score": self.overall_score,
            "recency_score": self.recency_score,
            "relevance_score": self.relevance_score,
            "popularity_score": self.popularity_score,
            "calculated_at": self.calculated_at,
        }


@dataclass
class PaperRelation:
    source_paper_id: str
    target_paper_id: str
    similarity_score: float = 0.0
    similarity_type: SimilarityType = SimilarityType.COMBINED
    calculated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, object]:
        return {
            "source_paper_id": self.source_paper_id,
            "target_paper_id": self.target_paper_id,
            "similarity_score": self.similarity_score,
            "similarity_type": self.similarity_type.value,
            "calculated_at": self.calculated_at,
        }


@dataclass
class PaperNotification:
    id: Optional[int] = None
    user_id: int = 0
    paper_id: str = ""
    paper_title: str = ""
    paper_url: str = ""
    notification_type: NotificationType = NotificationType.NEW_PAPER
    is_read: bool = False
    is_dismissed: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    delivered_at: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "paper_id": self.paper_id,
            "paper_title": self.paper_title,
            "paper_url": self.paper_url,
            "notification_type": self.notification_type.value,
            "is_read": self.is_read,
            "is_dismissed": self.is_dismissed,
            "created_at": self.created_at,
            "delivered_at": self.delivered_at,
        }


@dataclass
class PaperSnapshot:
    id: str
    source: str
    title: str
    authors: List[str]
    summary: str
    url: str
    published_at: str
    primary_category: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    snapshot_at: str = field(default_factory=lambda: datetime.now().isoformat())
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
            "primary_category": self.primary_category,
            "categories": self.categories,
            "snapshot_at": self.snapshot_at,
            "metadata": self.metadata,
        }

    @classmethod
    def from_paper_article(cls, paper: "PaperArticle") -> "PaperSnapshot":
        return cls(
            id=paper.id,
            source=paper.source,
            title=paper.title,
            authors=paper.authors,
            summary=paper.summary,
            url=paper.url,
            published_at=paper.published_at,
            primary_category=paper.metadata.get("primary_category"),
            categories=paper.metadata.get("categories", []),
            metadata=paper.metadata,
        )


@dataclass
class CategoryStats:
    category: str
    date_bucket: str
    paper_count: int = 0
    top_authors: List[str] = field(default_factory=list)
    hot_keywords: List[str] = field(default_factory=list)
    calculated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, object]:
        return {
            "category": self.category,
            "date_bucket": self.date_bucket,
            "paper_count": self.paper_count,
            "top_authors": self.top_authors,
            "hot_keywords": self.hot_keywords,
            "calculated_at": self.calculated_at,
        }


@dataclass
class UserMetadata:
    user_id: int
    last_login_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_notification_check_at: Optional[str] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "user_id": self.user_id,
            "last_login_at": self.last_login_at,
            "last_notification_check_at": self.last_notification_check_at,
        }
