from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src.clients.arxiv_client import fetch_arxiv_articles
from src.models.article import PaperArticle
from src.services.result_formatter import format_fetch_result
import traceback

SOURCE_TIMEOUT_SECONDS = 4
SOURCE_TIMEOUT_ERROR_MESSAGE = "arXiv request timed out. Please retry."
SOURCE_GENERIC_ERROR_MESSAGE = "Unable to load items from arXiv right now. Please retry."


class ListingContextKeys:
    """Canonical keys attached to fetch results for personalized discover context."""

    ACTIVE_INTEREST_KEYS = "active_interest_keys"
    BACKFILL_APPLIED = "backfill_applied"
    USED_DEFAULT_INTEREST_QUERY = "used_default_interest_query"


def _parse_published_timestamp(raw_timestamp: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def _normalized_categories(item: PaperArticle) -> set[str]:
    metadata = item.metadata
    categories = metadata.get("categories", [])
    normalized: set[str] = set()
    if isinstance(categories, list):
        normalized.update([str(value).strip().lower() for value in categories if str(value).strip()])
    primary = str(metadata.get("primary_category", "")).strip().lower()
    if primary:
        normalized.add(primary)
    return normalized


def _relevance_score(item: PaperArticle, interest_keys: list[str]) -> int:
    if not interest_keys:
        return 0
    interest_set = {key.strip().lower() for key in interest_keys if key.strip()}
    if not interest_set:
        return 0
    categories = _normalized_categories(item)
    return len(categories.intersection(interest_set))


def _rank_and_backfill_items(
    items: list[PaperArticle],
    interest_keys: list[str],
    minimum_result_count: int,
) -> tuple[list[PaperArticle], bool]:
    if not items:
        return [], False

    scored_items: list[tuple[int, datetime, PaperArticle]] = []
    for item in items:
        score = _relevance_score(item, interest_keys)
        published_at = _parse_published_timestamp(item.published_at)
        scored_items.append((score, published_at, item))

    scored_items.sort(
        key=lambda payload: (
            payload[0],
            payload[1],
            payload[2].id,
        ),
        reverse=True,
    )

    direct_matches = [entry for entry in scored_items if entry[0] > 0]
    fallback_matches = [entry for entry in scored_items if entry[0] == 0]

    selected: list[PaperArticle] = []
    for score, _, item in direct_matches:
        item.metadata["match_type"] = "direct"
        item.metadata["relevance_score"] = str(score)
        selected.append(item)

    backfill_applied = False
    for score, _, item in fallback_matches:
        if len(selected) >= minimum_result_count:
            break
        backfill_applied = True
        item.metadata["match_type"] = "backfill"
        item.metadata["relevance_score"] = str(score)
        selected.append(item)

    if not selected:
        return [], False

    return selected, backfill_applied


def _has_required_content(article: PaperArticle) -> bool:
    if not article.title.strip():
        return False
    if not article.summary.strip():
        return False
    if not article.authors:
        return False
    return PaperArticle.validate(article)


def _filter_valid_items(items: list[PaperArticle]) -> list[PaperArticle]:
    return [item for item in items if _has_required_content(item)]


def fetch_items(
    source: str,
    query: Optional[str] = None,
    limit: int = 10,
    interest_keys: Optional[list[str]] = None,
    minimum_result_count: int = 10,
) -> Dict[str, object]:
    source = source.lower()
    try:
        if source == "arxiv":
            items = fetch_arxiv_articles(limit=limit, query=query, timeout_seconds=SOURCE_TIMEOUT_SECONDS)
        else:
            return format_fetch_result(source, [], status="error", error_message="Unsupported source.")

        valid_items = _filter_valid_items(items)

        active_interest_keys = [key.strip().lower() for key in (interest_keys or []) if key.strip()]
        backfill_applied = False
        if active_interest_keys:
            ranked_items, backfill_applied = _rank_and_backfill_items(
                valid_items,
                active_interest_keys,
                minimum_result_count=max(1, minimum_result_count),
            )
            valid_items = ranked_items

        if not valid_items:
            empty_result = format_fetch_result(source, [], status="empty", error_message=None)
            empty_result[ListingContextKeys.ACTIVE_INTEREST_KEYS] = active_interest_keys
            empty_result[ListingContextKeys.BACKFILL_APPLIED] = False
            empty_result[ListingContextKeys.USED_DEFAULT_INTEREST_QUERY] = bool(active_interest_keys)
            return empty_result

        result = format_fetch_result(source, valid_items, status="success")
        result[ListingContextKeys.ACTIVE_INTEREST_KEYS] = active_interest_keys
        result[ListingContextKeys.BACKFILL_APPLIED] = backfill_applied
        result[ListingContextKeys.USED_DEFAULT_INTEREST_QUERY] = bool(active_interest_keys)
        return result
    except TimeoutError:
        return format_fetch_result(source, [], status="error", error_message=SOURCE_TIMEOUT_ERROR_MESSAGE)    
    except Exception as e:
        # 1. In toàn bộ "dấu vết" lỗi ra Console để bạn nhìn thấy
        print("--- DEBUG ARXIV ERROR ---")
        traceback.print_exc() 
        print("-------------------------")
        
        # 2. Bạn cũng có thể đưa chi tiết lỗi vào error_message để frontend/API hiển thị
        debug_message = f"{SOURCE_GENERIC_ERROR_MESSAGE} Chi tiết: {str(e)}"
        return format_fetch_result(source, [], status="error", error_message=debug_message)        
        #return format_fetch_result(source, [], status="error", error_message=SOURCE_GENERIC_ERROR_MESSAGE)
    
