# Data Model: User Interest Selection Onboarding

**Feature**: 009-build-user-interest-onboarding  
**Date**: 2026-06-08

## Entity: InterestTopic

Catalog-defined selectable interest.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `key` | string | Primary key, stable | Used in preference records and matching |
| `label` | string | Required, unique | User-facing display value |
| `is_active` | boolean | Required | False indicates retired topic |
| `is_default` | boolean | Required | Eligible for auto-fill defaults |
| `sort_order` | integer | Required | Presentation order |
| `updated_at` | string (ISO-8601) | Required | Catalog lifecycle auditing |

## Entity: UserInterestPreference

Account-owned preference set metadata for a user.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `user_id` | integer | PK/FK -> user_accounts.id | One preference set per user |
| `onboarding_completed` | boolean | Required | Gate for discovery access |
| `last_updated_at` | string (ISO-8601) | Required | Used for auditing and UX hints |

## Entity: UserInterestSelection

Join entity between user and interest topics.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | integer | Primary key | Internal row identifier |
| `user_id` | integer | Required, FK -> user_accounts.id | Owner |
| `interest_key` | string | Required, FK -> interest_topics.key | Selected topic |
| `created_at` | string (ISO-8601) | Required | Selection timestamp |

## Relationships

- One `UserInterestPreference` belongs to one `UserAccount`.
- One `UserInterestPreference` has many `UserInterestSelection` rows.
- One `InterestTopic` can be selected by many users.

## Validation Rules

- User must have between 3 and 10 active selected interests.
- Interest selections must come only from active catalog topics.
- Duplicate `(user_id, interest_key)` selections are disallowed.
- Unauthenticated requests cannot read or mutate preference entities.
- If retired-interest cleanup drops a user below minimum count, system default interests are auto-added until minimum is restored.

## State Transitions

1. `NeedsOnboarding` -> `OnboardingCompleted` when valid preference selection is submitted.
2. `OnboardingCompleted` -> `OnboardingCompleted` when user updates interests validly.
3. `OnboardingCompleted` -> `NeedsAutofill` when retired-topic cleanup drops selection count below minimum.
4. `NeedsAutofill` -> `OnboardingCompleted` when system default interests restore minimum count.
5. `Any` -> `Deleted` when user account is deleted (cascade remove preference + selections).

## Indexing and Integrity

- Unique index on `interest_topics.label`.
- Unique composite index on `user_interest_selections(user_id, interest_key)`.
- Index on `user_interest_selections(user_id)` for fast user preference reads.
- Foreign key cascade from preferences/selections to `user_accounts`.
