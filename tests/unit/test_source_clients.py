from datetime import datetime, timezone
from types import SimpleNamespace

from src.clients import arxiv_client


class _FakeClient:
    def __init__(self, *_args, **_kwargs):
        return

    def results(self, _search):
        entry = SimpleNamespace(
            entry_id="http://arxiv.org/abs/1234.5678v1",
            title="Example Paper Title",
            summary="This is a sample abstract.",
            authors=[SimpleNamespace(name="Jane Doe")],
            published=datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc),
            primary_category="cs.AI",
            get_short_id=lambda: "1234.5678v1",
        )
        return [entry]


def test_fetch_arxiv_articles(monkeypatch):
    fake_arxiv_module = SimpleNamespace(
        Search=lambda **_kwargs: object(),
        Client=_FakeClient,
        SortCriterion=SimpleNamespace(SubmittedDate="submitted"),
        SortOrder=SimpleNamespace(Descending="descending"),
    )
    monkeypatch.setattr(arxiv_client, "arxiv", fake_arxiv_module)

    results = arxiv_client.fetch_arxiv_articles(limit=1, query="ai")

    assert len(results) == 1
    assert results[0].id == "1234.5678v1"
    assert results[0].source == "arxiv"
    assert results[0].title == "Example Paper Title"
    assert results[0].authors == ["Jane Doe"]
    assert results[0].url == "https://arxiv.org/abs/1234.5678v1"
