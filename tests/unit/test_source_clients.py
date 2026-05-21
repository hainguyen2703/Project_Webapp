from unittest.mock import Mock, patch

from src.clients import arxiv_client, academia_client

ARXIV_SAMPLE_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/1234.5678v1</id>
    <title>Example Paper Title</title>
    <summary>This is a sample abstract.</summary>
    <published>2026-05-01T12:00:00Z</published>
    <author><name>Jane Doe</name></author>
    <arxiv:primary_category term="cs.AI" />
  </entry>
</feed>
'''

ACADEMIA_SAMPLE_HTML = '''<html><body>
  <div data-document-id="12345678">
    <h3><a class="document-title" href="/12345678/Example_Paper_Title">
      Example Paper Title
    </a></h3>
    <span class="author-name">Jane Smith</span>
    <p class="preview">A short excerpt about machine learning research.</p>
    <time datetime="2025-01-15">January 15, 2025</time>
  </div>
</body></html>
'''


@patch("src.clients.arxiv_client.requests.get")
def test_fetch_arxiv_articles(mock_get: Mock):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = ARXIV_SAMPLE_XML
    mock_get.return_value = mock_response

    results = arxiv_client.fetch_arxiv_articles(limit=1)

    assert len(results) == 1
    assert results[0].id == "http://arxiv.org/abs/1234.5678v1"
    assert results[0].source == "arxiv"
    assert results[0].title == "Example Paper Title"
    assert results[0].authors == ["Jane Doe"]


@patch("src.clients.academia_client.requests.get")
def test_fetch_academia_articles(mock_get: Mock):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = ACADEMIA_SAMPLE_HTML
    mock_get.return_value = mock_response

    results = academia_client.fetch_academia_articles(limit=1)

    assert len(results) == 1
    assert results[0].source == "academia"
    assert results[0].source_label == "Academia.edu"
    assert results[0].title == "Example Paper Title"
    assert results[0].authors == ["Jane Smith"]
    assert "excerpt" in results[0].summary or "machine learning" in results[0].summary
    assert "2025" in results[0].published_at
    assert "academia.edu" in results[0].url

