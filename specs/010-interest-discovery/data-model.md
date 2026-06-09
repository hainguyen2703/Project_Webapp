# Data Model: Interest-Based Discover

**Feature**: 010-interest-discovery  
**Date**: 2026-06-09

## Entity: DiscoverPreferenceContext

Effective personalization context for the current authenticated user.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `user_id` | integer | Required, FK -> user_accounts.id | Context owner |
| `effective_interest_keys` | list[string] | Required, min 3 | Active keys after retired-interest reconciliation and auto-fill |
| `retired_interest_keys` | list[string] | Optional | Keys removed during reconciliation for transparency/messaging |
| `minimum_required` | integer | Required, fixed = 3 | Validation boundary for valid personalization |
| `last_reconciled_at` | string (ISO-8601) | Required | Traceability for current effective context |

## Entity: DiscoverCandidateItem

Intermediate result item before final response shaping.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `item_id` | string | Required | Stable content identifier |
| `published_at` | string (ISO-8601/date-like) | Required | Recency ordering input |
| `primary_category` | string | Optional | Strong relevance signal when present |
| `all_categories` | list[string] | Optional | Additional matching signals |
| `relevance_score` | integer | Required, >= 0 | Higher score means stronger interest alignment |
| `match_type` | enum(`direct`,`backfill`) | Required | Indicates whether item matched effective interests directly |

## Entity: DiscoverResultSet

Final user-visible result payload for a Discover request.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `source` | string | Required | Currently `arxiv` |
| `items` | list[DiscoverCandidateItem] | Required | Ordered output list for rendering/API |
| `used_default_interest_query` | boolean | Required | True when no manual query override is supplied |
| `active_interest_keys` | list[string] | Required when defaults applied | Displayed to explain personalization context |
| `backfill_applied` | boolean | Required | True when broader recent papers were used to reach minimum result count |
| `status` | enum(`success`,`empty`,`error`) | Required | Existing response status envelope |

## Relationships

- One `DiscoverPreferenceContext` belongs to one authenticated `UserAccount`.
- One `DiscoverResultSet` is produced for one request using one `DiscoverPreferenceContext` (when defaults apply).
- `DiscoverResultSet.items` contains many `DiscoverCandidateItem` rows derived from source fetch output.

## Validation Rules

- Effective interests must contain at least 3 active keys after reconciliation.
- Default personalization is applied only for authenticated users with completed onboarding and no manual query override.
- Direct match eligibility uses OR semantics across effective interest keys.
- Ordering for default personalized results is relevance descending, then recency descending.
- Sparse direct matches trigger backfill with broader recent items until minimum default result count is reached.
- Cross-user context access is forbidden; all context and results are derived from current authenticated user only.

## State Transitions

1. `ContextPending` -> `ContextReady` when active interests are loaded and reconciled.
2. `ContextReady` -> `DefaultQueryApplied` when no manual query override is provided.
3. `DefaultQueryApplied` -> `RankedDirectResults` after relevance/recency ordering of direct matches.
4. `RankedDirectResults` -> `BackfilledResults` when direct-match count is below fixed minimum result count.
5. `BackfilledResults` -> `Rendered` when output is packaged with active-interest visibility metadata.

## Indexing and Integrity Considerations

- Reuse existing `ix_user_interest_owner` and `ux_user_interest_owner_key` indexes for low-latency preference retrieval.
- Keep interest topic key lookups indexed through `interest_topics.key` PK for reconciliation and labeling.
- Preserve foreign-key cascade integrity to ensure deleted accounts cannot leak stale preference context.
