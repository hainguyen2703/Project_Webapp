# Implementation Plan: Advanced Paper Features

**Branch**: `012-advanced-paper-features` | **Date**: 2026-06-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/012-advanced-paper-features/spec.md`

## Summary

Implement 5 advanced features to maximize paper discovery value: (P1) 1-5 star "Worth Reading" score based on recency/relevance/popularity, (P2) related papers via TF-IDF text similarity in detail page sidebar, (P2) duplicate paper detection with badges, (P3) new paper in-app notifications via APScheduler background jobs, (P3) trend analytics page using pandas with paper counts/top authors/hot keywords. Extends existing Flask app with paper persistence, text similarity, background jobs, and TDD-based development.

## Technical Context

**Language/Version**: Python 3.x  
**Primary Dependencies**: Flask, Flask-Login, sqlite3 (stdlib), arxiv client wrapper, pytest, scikit-learn (for TF-IDF), pandas (for trend analytics), APScheduler (for background notification jobs)  
**Storage**: SQLite (extend existing DB with `paper_snapshots`, `paper_notifications`, `category_stats`, `user_metadata`, `paper_relations`, `paper_scores` tables via `src/services/db.py`)  
**Testing**: pytest unit + integration tests via Flask test client; **TDD required - failing tests first**  
**Target Platform**: Server-rendered Flask web app on local dev and WSGI-compatible runtime  
**Project Type**: Single-project web application  
**Performance Goals**: Align with spec: "Worth Reading" score display <1s, related papers <2s, duplicate detection 95% accurate, analytics page <5s load, background job overhead <10s/day  
**Constraints**: Server-side only rendering, no external citation data, APScheduler for periodic background notification checks, scikit-learn TF-IDF + pandas for analytics, 1-5 star display with weighted scoring (40% recency, 35% relevance, 25% popularity), **strict TDD methodology**  
**Scale/Scope**: Existing single-node app; features built incrementally by priority with clear separation between P1/P2/P3 deliverables

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design | Post-Design |
|-----------|------------|-------------|
| I. Code Quality & Maintainability | PASS - features can be delivered with new dedicated service module, focused DB extensions, and targeted template changes; TDD ensures high quality | PASS - research defines clear algorithmic approaches, data model separates concerns, TDD methodology ensures maintainable code, and implementation plan maintains existing architecture boundaries |
| II. User Experience Consistency | PASS - features extend existing paper viewing flows with predictable UI elements and clear onboarding for analytics/notification features | PASS - contracts and quickstart define consistent visual patterns for badges, scores, notifications, and analytics display that align with existing UI |
| III. Performance Requirements | PASS - spec includes measurable latency targets; similarity/scoring can be optimized with caching and async precomputation if needed | PASS - design uses background jobs via APScheduler for notifications (avoids blocking login), pandas for efficient trend calculations, and SQLite for persistent storage suitable for current scale |

**Gate result**: PASS. No constitutional violations requiring exceptions.

## Project Structure

### Documentation (this feature)

```text
specs/012-advanced-paper-features/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── app.py                              # MODIFY: add /analytics route; extend detail, listing, login routes; add APScheduler initialization
├── models/
│   ├── article.py                      # MODIFY: extend with score calculation helpers
│   └── advanced_features.py            # NEW: PaperScore, PaperRelation, PaperNotification, PaperSnapshot, CategoryStats, UserMetadata models
├── services/
│   ├── db.py                           # MODIFY: add DB tables and CRUD for new entities
│   ├── advanced_service.py             # NEW: scoring, similarity, notification check, analytics logic (using pandas)
│   ├── scheduler_service.py            # NEW: APScheduler setup and background job definitions
│   └── discovery_service.py            # VERIFY/MODIFY: integrate duplicate detection
├── templates/
│   ├── detail.html                     # MODIFY: add score display and related papers sidebar
│   ├── home.html                       # MODIFY: add duplicate badges to listings
│   ├── discover.html                   # MODIFY: add duplicate badges to listings
│   ├── base.html                       # MODIFY: add notification UI component
│   └── analytics.html                  # NEW: analytics page template
└── static/
    └── styles.css                      # MODIFY: styles for badges, stars, notifications

tests/
├── unit/
│   └── test_advanced_features.py       # NEW: TDD unit tests (fail first!)
└── integration/
    └── test_advanced_features_flow.py  # NEW: TDD integration tests (fail first!)

requirements.txt                        # MODIFY: add scikit-learn, pandas, APScheduler
```

**Structure Decision**: Continue within existing single Flask project. Create new `src/services/advanced_service.py` for core feature logic, `src/services/scheduler_service.py` for APScheduler background job management. Keep route orchestration in `src/app.py`, data model in `src/models/`, DB access in `src/services/db.py`, and templates focused on presentation only. **Follow TDD strictly - always write failing tests first!** Deliver incrementally by user story priority (P1 first, then P2, then P3).

## Complexity Tracking

No constitutional violations requiring justification. APScheduler adds minimal operational complexity, pandas/scikit-learn are standard Python libraries with low learning curve given existing Flask stack.
