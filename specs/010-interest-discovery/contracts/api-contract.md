# API Contract: Interest-Based Discover (v1)

**Feature**: 010-interest-discovery  
**Date**: 2026-06-09

## Scope

Defines externally observable behavior for personalized Discover defaults, ordering, sparse-result backfill, and active-interest transparency in existing web and API discovery endpoints.

## Route: GET /

Primary server-rendered Discover page.

### Auth and onboarding behavior

- Unauthenticated users: existing anonymous discovery behavior remains available.
- Authenticated users with incomplete onboarding: redirected to `/onboarding/interests`.
- Authenticated onboarded users with no `query` and `fetch=1`: defaults are built from effective user interests.

### Default personalization behavior

When defaults are applied:
- Eligible papers are those matching any effective interest key (OR semantics).
- Result ordering is interest relevance first, then recency.
- If direct matches are below fixed minimum result count, broader recent papers are appended as backfill.
- Template context includes active interest keys and whether default-interest mode was used.

### Manual override behavior

- If `query` is provided, manual query takes precedence and interest default personalization is not injected.

## Route: GET /api/listings

Machine-consumable listing endpoint for discovery.

### Request

Query params:
- `source` (required)
- `query` (optional)

### Response envelope

Existing envelope retained:
- `source`
- `status` (`success|empty|error`)
- `items`
- `error_message`
- `fetched_at`

### Personalization semantics

- If authenticated + onboarded + `query` absent: apply interest defaults.
- If `query` present: skip defaults and use provided query.
- Default-mode responses MUST respect OR eligibility and relevance-then-recency ordering.
- Sparse default-mode responses MUST include backfill items after direct matches to reach configured minimum count.

## Route: GET /onboarding/interests

No contract change from feature 009, but remains required precondition for authenticated users without completed onboarding before normal personalized Discover defaults can apply.

## Privacy and ownership contract

- Personalization context MUST be derived only from current authenticated user account.
- No endpoint may expose another user’s interests or effective context.

## Retired interest lifecycle contract

- Retired interests are removed from effective context before default personalization.
- If effective context falls below 3 interests, system default interests are auto-added before generating default Discover results.

## Compatibility constraints

- Existing endpoint paths and status envelope shapes remain backward-compatible.
- Existing auth/login/logout/register workflows remain unchanged.
- Existing favorites/detail flows remain unchanged except receiving differently ordered/defaulted listing results.
