from typing import Dict, List, Optional

from src.models.article import PaperArticle


def format_fetch_result(source: str, items: List[PaperArticle], status: str = "success", error_message: Optional[str] = None) -> Dict[str, object]:
    fetched_at = items[0].fetched_at if items else None
    return {
        "source": source,
        "status": status,
        "items": [item.to_dict() for item in items],
        "error_message": error_message,
        "fetched_at": fetched_at,
    }
