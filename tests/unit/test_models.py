import pytest

from src.models.article import PaperArticle


def test_paper_article_to_dict_and_validate():
    article = PaperArticle(
        id="1234.5678v1",
        source="arxiv",
        title="Sample Title",
        authors=["Jane Doe"],
        summary="A brief summary.",
        url="https://arxiv.org/abs/1234.5678v1",
        published_at="2026-05-01T12:00:00+00:00",
        source_label="arXiv",
        fetched_at="2026-05-01T12:10:00+00:00",
    )

    data = article.to_dict()

    assert data["id"] == "1234.5678v1"
    assert data["source"] == "arxiv"
    assert data["url"] == "https://arxiv.org/abs/1234.5678v1"
    assert PaperArticle.validate(article) is True


def test_paper_article_validate_rejects_invalid_url():
    article = PaperArticle(
        id="test-2",
        source="medium",
        title="Sample Title",
        authors=["Jane Doe"],
        summary="A brief summary.",
        url="not-a-url",
        published_at="2026-05-01T12:00:00+00:00",
        source_label="Medium",
        fetched_at="2026-05-01T12:10:00+00:00",
    )

    assert PaperArticle.validate(article) is False
