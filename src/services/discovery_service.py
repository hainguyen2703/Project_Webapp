from typing import Dict, Optional

from src.clients.arxiv_client import fetch_arxiv_articles
from src.clients.academia_client import fetch_academia_articles
from src.services.result_formatter import format_fetch_result
from src.models.article import PaperArticle


def fetch_items(source: str, query: Optional[str] = None, limit: int = 10) -> Dict[str, object]:
    source = source.lower()
    try:
        if source == "arxiv":
            items = fetch_arxiv_articles(limit=limit, query=query)
        elif source == "academia":
            items = fetch_academia_articles(limit=limit, query=query)
        else:
            return format_fetch_result(source, [], status="error", error_message="Unsupported source.")

        if not items:
            return format_fetch_result(source, [], status="empty", error_message=None)

        return format_fetch_result(source, items, status="success")
    except Exception as exc:
        return format_fetch_result(source, [], status="error", error_message=str(exc))
