from unittest.mock import Mock, patch

from src.clients import arxiv_client

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

