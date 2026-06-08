# API Contract: User Interest Selection Onboarding (v1)

**Feature**: 009-build-user-interest-onboarding  
**Date**: 2026-06-08

## Scope

Defines externally observable behavior for onboarding-gated interest preference flows and interest-driven discovery defaults.

## Route: GET /onboarding/interests

Renders interest onboarding for authenticated users with incomplete onboarding.

### Auth Behavior

- Unauthenticated: redirects to login (existing auth pattern).
- Authenticated + onboarding incomplete: returns `200` onboarding page.
- Authenticated + onboarding complete: redirects to discovery/home.

## Route: POST /onboarding/interests

Saves initial interest selections and marks onboarding complete.

### Request

Form payload:
- `interest_keys[]` (required): 3-10 values from active catalog

### Validation

- Reject if count < 3 or > 10.
- Reject if any key is not active catalog member.
- Reject duplicate keys.

### Response

- Success: redirect `302/303` to discovery/home.
- Validation failure: `200` onboarding page with field/form errors.

## Route: GET /interests

Renders interest management view for authenticated users.

### Auth Behavior

- Unauthenticated: redirects to login.
- Authenticated + onboarding complete: returns `200` with pre-populated current selections.
- Authenticated + onboarding incomplete: redirects to `/onboarding/interests`.

## Route: POST /interests

Updates an onboarded user's selected interests.

### Request

Form payload:
- `interest_keys[]` (required): 3-10 active catalog keys

### Response

- Success: `302/303` redirect to management/discovery context.
- Validation failure: `200` with user-facing validation errors.

## Discovery Default Contract

For authenticated users with completed onboarding and no manual override:
- Discovery defaults MUST apply OR matching across selected interests.
- Any paper matching at least one selected interest is eligible.

For users with incomplete onboarding:
- Discovery routes MUST redirect to `/onboarding/interests`.

## Retired Interest Lifecycle Contract

When catalog topics are retired:
- Retired topics are automatically removed from user selections.
- If user selection count drops below minimum, system default topics are auto-added until minimum is met.

## Account Deletion Contract

Deleting a user account MUST remove:
- onboarding/preference metadata
- all user interest selections

## Compatibility Constraints

- Existing authentication flow remains intact.
- Existing discovery route contract remains intact except for new onboarding gate and default-filter behavior.
