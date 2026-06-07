from typing import Dict, Optional

from src.clients.arxiv_client import fetch_arxiv_articles
from src.models.article import PaperArticle
from src.services.result_formatter import format_fetch_result
import traceback

SOURCE_TIMEOUT_SECONDS = 4
SOURCE_TIMEOUT_ERROR_MESSAGE = "arXiv request timed out. Please retry."
SOURCE_GENERIC_ERROR_MESSAGE = "Unable to load items from arXiv right now. Please retry."


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


def fetch_items(source: str, query: Optional[str] = None, limit: int = 10) -> Dict[str, object]:
    source = source.lower()
    try:
        if source == "arxiv":
            items = fetch_arxiv_articles(limit=limit, query=query, timeout_seconds=SOURCE_TIMEOUT_SECONDS)
        else:
            return format_fetch_result(source, [], status="error", error_message="Unsupported source.")

        valid_items = _filter_valid_items(items)

        if not valid_items:
            return format_fetch_result(source, [], status="empty", error_message=None)

        return format_fetch_result(source, valid_items, status="success")
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
    
