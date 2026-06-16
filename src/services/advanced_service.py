from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, Optional, List, Dict
from collections import Counter
import logging

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from .db import (
    save_paper_snapshot, list_paper_snapshots, get_paper_snapshot,
    save_paper_score, get_paper_score,
    save_paper_relation, get_related_papers,
    save_category_stats, get_category_stats,
    list_user_notifications, add_paper_notification,
    get_user_metadata, upsert_user_metadata,
    list_user_interest_keys
)

logger = logging.getLogger(__name__)


def calculate_recency_score(published_at_str: str) -> float:
    """Calculate recency score from 0 (very old) to 5 (very new)"""
    try:
        published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        delta = now - published_at
        days = max(delta.days, 0)
        # Exponential decay: score 5 at 0 days, 0 at ~365 days
        score = 5.0 * (2.718 ** (-days / 90.0))  # Half-life ~60 days
        return min(max(score, 0.0), 5.0)
    except Exception:
        return 2.5

#Hàm đánh giá điểm của paper dựa theo độ tương thích với các chủ đề quan tâm của 1 user cụ thể
def calculate_relevance_score(paper_categories: List[str], user_interest_keys: List[str]) -> float:
    """Calculate relevance score from 0 to 5 based on category match"""
    if not user_interest_keys or not paper_categories:
        return 2.5
    paper_cat_set = set(paper_categories)
    user_cat_set = set(user_interest_keys)
    overlap = len(paper_cat_set & user_cat_set)
    score = (overlap / max(len(user_cat_set), 1)) * 5.0
    return min(max(score, 0.0), 5.0)

#Đánh giá dựa trên các chủ đề hot, nếu paper thuộc vào chủ đề hot sẽ điểm cao
def calculate_popularity_score(category: Optional[str]) -> float:
    """Calculate popularity score from 0 to 5 based on category size"""
    # For MVP, use fixed scores based on category type
    popular_categories = {"cs.AI", "cs.LG", "cs.CV", "cs.CL", "cs.se"}
    if category in popular_categories:
        return 4.5
    return 2.5

#Hàm tính toán điểm đáng đọc của paper đối với user
#Nghĩa là điểm số được customize theo user, không phản ánh general
def calculate_worth_reading_score(
    published_at: str,
    paper_categories: List[str],
    user_interest_keys: List[str],
    primary_category: Optional[str] = None
) -> Dict[str, float]:
    """Calculate overall worth reading score and components"""
    recency = calculate_recency_score(published_at) #Lấy điểm theo độ mới (ngày viết) của paper
    relevance = calculate_relevance_score(paper_categories, user_interest_keys) #Lấy điểm theo tương thích với sở thích của user
    popularity = calculate_popularity_score(primary_category) #Lấy điểm của paper theo chủ đề hot
    #Tính điểm: ưu tiên đúng chủ đề quan tâm, chủ đề hot, ngày viêt
    overall = 0.25 * recency + 0.4 * relevance + 0.35 * popularity
    return {
        "overall_score": overall,
        "recency_score": recency,
        "relevance_score": relevance,
        "popularity_score": popularity
    }


def score_to_stars(score: float) -> int:
    """Convert score (0-5) to integer stars (1-5)"""
    return max(1, min(5, int(round(score))))


def calculate_similarity(texts: List[str]) -> Optional[List[List[float]]]:
    """Calculate cosine similarity matrix using TF-IDF (scikit-learn)"""
    if not HAS_SKLEARN or not texts:
        return None
    try:
        vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        tfidf_matrix = vectorizer.fit_transform(texts)
        return cosine_similarity(tfidf_matrix).tolist()
    except Exception as e:
        logger.warning("Failed to calculate similarity: %s", e)
        return None


def compute_and_store_related_papers() -> None:
    """Compute related papers for all stored snapshots and store them in DB"""
    all_snapshots = list_paper_snapshots(limit=100)
    if len(all_snapshots) < 2:
        logger.info("Not enough snapshots to compute related papers yet")
        return

    paper_ids = [s["id"] for s in all_snapshots]
    paper_texts = [
        (s["title"] + " " + s["summary"])
        for s in all_snapshots
    ]
    similarity_matrix = calculate_similarity(paper_texts)
    if similarity_matrix is None:
        logger.info("Could not compute similarity, skipping")
        return

    # Now for each paper, find top 3 similar papers
    for i in range(len(all_snapshots)):
        source_paper_id = paper_ids[i]
        # Collect similarity scores for all other papers
        similarities = []
        for j in range(len(all_snapshots)):
            if i == j:
                continue
            target_paper_id = paper_ids[j]
            sim_score = similarity_matrix[i][j]
            if sim_score > 0.05:  # Lowered threshold to get more related papers
                similarities.append((target_paper_id, sim_score))
        # Sort and keep top 3
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_related = similarities[:3]
        for target_paper_id, sim_score in top_related:
            save_paper_relation(
                source_paper_id=source_paper_id,
                target_paper_id=target_paper_id,
                similarity_score=sim_score,
                similarity_type="combined"
            )
    logger.info("Successfully computed and stored related papers")


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Extract simple keywords from text for hot topics (no scikit-learn needed)"""
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    stopwords = {
        "the", "and", "for", "with", "that", "this", "from", "have", "has", "but",
        "not", "are", "or", "by", "your", "you", "our", "we", "they", "them", "their",
        "can", "will", "into", "than", "then", "also", "more", "most", "very", "just"
    }
    filtered = [w for w in words if w not in stopwords]
    counter = Counter(filtered)
    return [k for k, _ in counter.most_common(top_n)]


def calculate_analytics(category: Optional[str] = None) -> Dict[str, Any]:
    """Calculate trend analytics using pandas if available"""
    snapshots = list_paper_snapshots(category=category, limit=100)
    if not snapshots:
        return {"paper_counts": {}, "top_authors": [], "hot_keywords": []}

    # Paper count trends (group by date)
    date_counts = {}
    all_authors = []
    all_text = ""
    for snap in snapshots:
        pub_date = snap["published_at"][:10]  # YYYY-MM-DD
        date_counts[pub_date] = date_counts.get(pub_date, 0) + 1
        all_authors.extend(snap["authors"])
        all_text += " " + snap["title"] + " " + snap["summary"]

    # Top authors
    author_counts = Counter(all_authors)
    top_authors = [a for a, c in author_counts.most_common(10)]
    # Hot keywords
    hot_keywords = extract_keywords(all_text, top_n=15)

    return {
        "paper_counts": sorted(date_counts.items()),
        "top_authors": top_authors,
        "hot_keywords": hot_keywords
    }


def check_new_papers_for_user(user_id: int) -> List[Dict[str, Any]]:
    """Check for new papers matching user interests since last check"""
    user_interests = list_user_interest_keys(user_id=user_id)
    user_meta = get_user_metadata(user_id=user_id)
    since = user_meta["last_notification_check_at"] if user_meta else None
    new_papers = []
    for interest in user_interests:
        snaps = list_paper_snapshots(category=interest, since=since, limit=10)
        new_papers.extend(snaps)
    # Update last check time
    upsert_user_metadata(
        user_id=user_id,
        last_notification_check_at=datetime.now(timezone.utc).isoformat()
    )
    return new_papers
