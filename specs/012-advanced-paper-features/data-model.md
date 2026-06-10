# Data Model: Advanced Paper Features

## Entities

### PaperScore
- `paper_id`: string (references PaperArticle.id)
- `user_id`: int? (optional, for user-specific relevance scoring)
- `overall_score`: float (0.0 - 5.0)
- `recency_score`: float (0.0 - 5.0)
- `relevance_score`: float (0.0 - 5.0)
- `popularity_score`: float (0.0 - 5.0)
- `calculated_at`: string (ISO 8601)

### PaperRelation
- `source_paper_id`: string (references PaperArticle.id)
- `target_paper_id`: string (references PaperArticle.id)
- `similarity_score`: float (0.0 - 1.0)
- `similarity_type`: enum(`title`, `summary`, `combined`)
- `calculated_at`: string (ISO 8601)

### PaperNotification
- `id`: int (primary key)
- `user_id`: int (references AuthUser.id)
- `paper_id`: string (references PaperArticle.id)
- `paper_title`: string
- `paper_url`: string
- `notification_type`: enum(`new_paper`)
- `is_read`: boolean
- `is_dismissed`: boolean
- `created_at`: string (ISO 8601)
- `delivered_at`: string? (ISO 8601, when shown to user)

### PaperSnapshot
- `id`: string (same as PaperArticle.id)
- `source`: string (`arxiv` or `medium`)
- `title`: string
- `authors`: string[]
- `summary`: string
- `url`: string
- `published_at`: string (ISO 8601)
- `primary_category`: string?
- `categories`: string[]
- `snapshot_at`: string (ISO 8601, when persisted)
- `metadata`: object (optional source-specific fields)

### CategoryStats
- `category`: string
- `date_bucket`: string (e.g., "2026-W23", "2026-06")
- `paper_count`: int
- `top_authors`: string[] (array of author names, ordered by count)
- `hot_keywords`: string[] (array of trending keywords)
- `calculated_at`: string (ISO 8601)

### UserMetadata
- `user_id`: int (references AuthUser.id, unique)
- `last_login_at`: string (ISO 8601)
- `last_notification_check_at`: string? (ISO 8601)

## Relationships
- PaperScore relates to one PaperArticle (paper_id) and optionally one AuthUser (user_id)
- PaperRelation relates two PaperArticle entities (source and target)
- PaperNotification relates to one AuthUser (user_id) and one PaperArticle (paper_id)
- PaperSnapshot is a persisted copy of PaperArticle for historical reference
- CategoryStats aggregates data about papers by category and time
- UserMetadata extends AuthUser with tracking for notifications

## Validation Rules
- PaperScore.overall_score MUST be the weighted average of recency_score, relevance_score, and popularity_score
- PaperRelation.similarity_score MUST be between 0.0 and 1.0
- PaperSnapshot.published_at MUST be a valid ISO 8601 timestamp
- UserMetadata.user_id MUST be unique and reference an existing AuthUser
- CategoryStats.paper_count MUST be >= 0

## Caching / Persistence Considerations
- PaperScore can be cached per user and refreshed periodically
- PaperRelation should be persisted in SQLite for quick lookup
- PaperSnapshot stores historical paper data for trend analytics
- PaperNotification must be persisted in SQLite with user database
- CategoryStats should be precomputed periodically (daily/weekly) and cached
- UserMetadata should be persisted in SQLite auth database
