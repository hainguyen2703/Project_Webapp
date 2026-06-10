# Research: Advanced Paper Features

**Feature**: 012-advanced-paper-features  
**Date**: 2026-06-10  
**Status**: Complete

## Decision 1: Text Similarity Algorithm for Related Papers & Duplicate Detection

**Decision**: Use TF-IDF (Term Frequency-Inverse Document Frequency) with cosine similarity from scikit-learn for comparing paper titles and summaries, plus vector embeddings as an optional enhancement. Also use normalized arXiv ID matching for exact duplicate detection.

**Rationale**: TF-IDF is well-understood, works well for short text like paper titles/abstracts; scikit-learn provides robust, standard implementation. Vector embeddings are optional but available for better accuracy if needed.

**Alternatives considered**:
- Jaccard similarity (word overlap): rejected as too simplistic and doesn't account for term importance.
- Sentence-BERT embeddings only: rejected as too heavy for MVP, but keep as option.
- Only category matching: rejected as less precise than content-based similarity.

## Decision 2: "Worth Reading" Score Calculation

**Decision**: Calculate score as weighted average: 40% recency, 35% relevance to user interests, 25% category popularity. Convert to 1-5 star display.

**Rationale**: Balances freshness, personalization, and general popularity. Weighting prioritizes recency slightly as users often care about recent papers.

**Alternatives considered**:
- Equal weights: rejected because recency is typically more important than category popularity.
- 100% relevance: rejected as it ignores temporal value and general interest signals.
- Citation-based: rejected as no citation data available from arXiv API.

## Decision 3: Paper Persistence Strategy

**Decision**: Create PaperSnapshot table to persist paper metadata for trend analytics and duplicate detection.

**Rationale**: Need historical paper data for calculating trends, storing category stats over time, and maintaining duplicate detection context between sessions.

**Alternatives considered**:
- No persistence, recompute everything: rejected as inefficient and unable to track trends over time.
- Full caching system: rejected as over-engineering; simple snapshot persistence sufficient.

## Decision 4: Trend Statistics Implementation

**Decision**: Use pandas for data aggregation and trend statistics generation (paper count trends, top authors, hot keywords).

**Rationale**: pandas is standard, powerful library for tabular data analysis and time-series trend calculation; integrates well with SQLite and Python.

**Alternatives considered**:
- Manual SQL aggregation only: rejected as less flexible and harder to maintain for complex trend calculations.
- External analytics tools: rejected as adds unnecessary complexity beyond current stack.

## Decision 5: Notification Delivery System

**Decision**: Use a background job scheduler (APScheduler for simplicity) to periodically check for new relevant papers, not just at login. Store notifications in PaperNotification table for display when users log in.

**Rationale**: APScheduler is lightweight, easy to integrate with Flask, doesn't require external infrastructure like Celery. Periodic background checks ensure notifications are ready when users log in, improving UX.

**Alternatives considered**:
- Login-time only checks: rejected as may miss papers published between logins, slower UX at login.
- Celery + Redis/RabbitMQ: rejected as overkill for current scale, adds operational complexity.
- System cron: rejected as less integrated with application lifecycle, harder to manage dynamically.

## Decision 6: Analytics Page Visualization Strategy

**Decision**: Use simple HTML/CSS with server-generated data for trend displays, using pandas for data prep. No heavy frontend charting library in v1, but structure data for easy future addition.

**Rationale**: Keeps tech stack consistent with existing server-rendered Flask app; pandas handles data heavy-lifting server-side. Can add charting libraries later if needed.

**Alternatives considered**:
- Chart.js/D3.js: rejected as adds frontend complexity not justified for v1.
- Export to CSV only: rejected as poor user experience for interactive exploration.

## Decision 7: Development Methodology

**Decision**: Follow Test-Driven Development (TDD) principles strictly: write failing tests first, then implement the minimal code to make them pass, then refactor.

**Rationale**: TDD ensures high code quality, comprehensive test coverage, and clear documentation of expected behavior; reduces regression risk as features are added incrementally.

**Alternatives considered**:
- Write tests after implementation: rejected as leads to incomplete coverage and tests tailored to existing implementation rather than requirements.
- No automated tests: rejected as high-risk for codebase maintainability.

## Decision 8: Duplicate Badge UI Placement

**Decision**: Display duplicate badge prominently next to paper title in search results and discover lists.

**Rationale**: Makes duplicates immediately visible without requiring user to hunt for them.

**Alternatives considered**:
- Hide duplicates entirely: rejected as user may want to see why something appeared twice.
- Only show badge on hover: rejected as not discoverable enough.

## Residual Risks

- TF-IDF similarity quality depends on having good summary text; papers with very short/non-English abstracts may have poor recommendations.
- Trend analytics are only as good as the historical data we can collect; early on, trend data will be limited.
- Notification quality depends on arXiv API returning truly new papers; arXiv sometimes re-indexes older papers which may appear as "new".
- Category popularity calculation needs sufficient paper volume per category to be meaningful; niche categories may have unstable popularity scores.
- APScheduler needs to be properly managed in production deployment (single worker, graceful shutdown, etc.).
