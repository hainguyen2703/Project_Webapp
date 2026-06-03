# Quickstart: Standardize arXiv Discovery Source

**Feature**: 007-rework-arxiv-lib  
**Date**: 2026-06-04

## Prerequisites

- Python 3.x
- pip

## Setup

```bash
cd d:/Project_Webapp
pip install -r requirements.txt
```

Dependency note: this feature now depends on the Python `arxiv` package for discovery retrieval.

## Run Application

```bash
python -m src.app
```

App URL: http://localhost:8000

## Validation Scenarios

### 1) Discovery success uses canonical metadata

1. Open `http://localhost:8000/?fetch=1`.
2. Confirm results render with title, authors, summary, published date, and source link.
3. Confirm each item identity is canonical arXiv ID in service payload.

### 2) Detail view required content

1. Open a result detail page from home results.
2. Confirm required fields render: title, authors, summary, publication date, canonical identifier, canonical link.
3. Confirm no missing required content for valid records.

### 3) Timeout and retry behavior

1. Simulate source timeout in arXiv client (or patch client to raise timeout).
2. Trigger discovery fetch.
3. Confirm retry-ready error state appears within 4 seconds.
4. Retry and confirm recovery when source is available.

### 4) Malformed required-field filtering

1. Simulate a source record with malformed required field(s).
2. Trigger discovery fetch.
3. Confirm malformed record is excluded.
4. Confirm other valid records still render.

### 5) Empty results behavior

1. Search using a query expected to return no valid matches.
2. Confirm explicit no-results state renders without error.

## Test Commands

```bash
pytest tests/unit/test_source_clients.py
pytest tests/integration/test_discovery_flow.py
pytest tests/
```

## Planned File Touchpoints

- `requirements.txt` (add `arxiv` dependency if not present)
- `src/clients/arxiv_client.py`
- `src/services/discovery_service.py`
- `src/models/article.py`
- `src/app.py` (only if identifier propagation adjustments are required)
- `tests/unit/test_source_clients.py`
- `tests/integration/test_discovery_flow.py`

## Expected Outcomes

- Discovery uses the Python arXiv library instead of manual XML parsing.
- Returned records follow one canonical metadata schema.
- Timeout, malformed-data filtering, and retry behavior satisfy specification success criteria.

## Validation Log

- Date: 2026-06-04
- Commands:
	- `python -m pytest tests/unit/test_source_clients.py tests/unit/test_models.py tests/integration/test_discovery_flow.py`
	- `python -m pytest tests/`
- Result: 38 passed, 0 failed
