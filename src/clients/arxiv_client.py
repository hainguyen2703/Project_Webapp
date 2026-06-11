from __future__ import annotations

import datetime
import re
import time
from typing import List, Optional

import arxiv

from src.models.article import PaperArticle

DEFAULT_QUERY = "cat:cs.AI"
REQUEST_TIMEOUT_SECONDS = 30
# Cache with timestamps to expire after 1 hour
CACHE: dict[str, tuple[float, List[PaperArticle]]] = {}
CACHE_EXPIRY_SECONDS = 3600  # 1 hour

_ARXIV_ID_PATTERNS = [
    re.compile(r"(\d{4}\.\d{4,5}(?:v\d+)?)$"),
    re.compile(r"([a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)$", re.IGNORECASE),
]


def _clean_summary(summary: str) -> str:
    """Clean up LaTeX-style math symbols in the summary."""
    # Replace common LaTeX symbols
    replacements = {
        r"$\pm$": "±",
        r"\pm": "±",
        r"$\mu$": "µ",
        r"\mu": "µ",
        r"$\alpha$": "α",
        r"\alpha": "α",
        r"$\beta$": "β",
        r"\beta": "β",
        r"$\gamma$": "γ",
        r"\gamma": "γ",
        r"$\delta$": "δ",
        r"\delta": "δ",
        r"$\epsilon$": "ε",
        r"\epsilon": "ε",
        r"$\theta$": "θ",
        r"\theta": "θ",
        r"$\lambda$": "λ",
        r"\lambda": "λ",
        r"$\pi$": "π",
        r"\pi": "π",
        r"$\sigma$": "σ",
        r"\sigma": "σ",
        r"$\tau$": "τ",
        r"\tau": "τ",
        r"$\phi$": "φ",
        r"\phi": "φ",
        r"$\omega$": "ω",
        r"\omega": "ω",
        r"$\infty$": "∞",
        r"\infty": "∞",
        r"$\le$": "≤",
        r"\le": "≤",
        r"$\leq$": "≤",
        r"\leq": "≤",
        r"$\ge$": "≥",
        r"\ge": "≥",
        r"$\geq$": "≥",
        r"\geq": "≥",
        r"$\times$": "×",
        r"\times": "×",
        r"$\neq$": "≠",
        r"\neq": "≠",
        r"$^\circ$": "°",
        r"\circ": "°",
        r"$\sim$": "~",
        r"\sim": "~",
        r"$": "",  # Remove remaining dollar signs
        r"\_": "_",
        r"\$": "$",
        r"\&": "&",
        r"\%": "%",
        r"\#": "#",
        r"\{": "{",
        r"\}": "}",
    }
    for latex, plain in replacements.items():
        summary = summary.replace(latex, plain)
    return summary


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



def fetch_arxiv_articles(limit: int = 50, query: Optional[str] = None, timeout_seconds: int = REQUEST_TIMEOUT_SECONDS) -> List[PaperArticle]:
    if arxiv is None:
        raise RuntimeError("Python package 'arxiv' is required for discovery retrieval.")

    search_query = _build_query(query)
    cache_key = f"{search_query}:{limit}"
    current_time = time.time()

    # Check cache for valid entry
    if cache_key in CACHE:
        timestamp, cached_results = CACHE[cache_key]
        if current_time - timestamp < CACHE_EXPIRY_SECONDS:
            return cached_results

    search = arxiv.Search(
        query=search_query,
        max_results=limit,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )
    client = arxiv.Client(page_size=min(limit, 100), delay_seconds=0.5, num_retries=3)
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
        summary = _clean_summary(str(getattr(result, "summary", "") or "").strip())
        raw_authors = getattr(result, "authors", []) or []
        authors = [str(getattr(author, "name", "") or "").strip() for author in raw_authors if str(getattr(author, "name", "") or "").strip()]
        published = _parse_iso(getattr(result, "published", ""))
        fetched_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        primary_category = str(getattr(result, "primary_category", "") or "").lower()
        raw_categories = getattr(result, "categories", []) or []
        categories = [str(value or "").strip().lower() for value in raw_categories if str(value or "").strip()]
        if primary_category and primary_category not in categories:
            categories.insert(0, primary_category)
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
            metadata={"primary_category": primary_category, "categories": categories},
        )
        results.append(article)

    CACHE[cache_key] = (current_time, results)
    return results


def fetch_single_paper(arxiv_id: str) -> Optional[dict]:
    """Fetch a single paper from arXiv by ID, return as a dict."""
    try:
        search = arxiv.Search(
            id_list=[arxiv_id],
            max_results=1
        )
        client = arxiv.Client(page_size=1, delay_seconds=0.1)
        for result in client.results(search):
            title = str(getattr(result, "title", "")).strip()
            summary = _clean_summary(str(getattr(result, "summary", "")).strip())
            raw_authors = getattr(result, "authors", [])
            authors = [str(a.name) for a in raw_authors]
            published = _parse_iso(getattr(result, "published", ""))
            primary_category = str(getattr(result, "primary_category", "")).lower()
            raw_categories = getattr(result, "categories", [])
            categories = [str(c).lower() for c in raw_categories]
            canonical_url = f"https://arxiv.org/abs/{arxiv_id}"

            paper_dict = {
                "id": arxiv_id,
                "source": "arxiv",
                "title": title,
                "authors": authors,
                "summary": summary,
                "url": canonical_url,
                "published_at": published,
                "source_label": "arXiv",
                "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "metadata": {
                    "primary_category": primary_category,
                    "categories": categories
                },
            }
            return paper_dict
    except Exception as e:
        print(f"Error fetching paper {arxiv_id}: {e}")
        return None
