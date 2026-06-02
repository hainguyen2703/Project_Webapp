# API Contract: User Login and Logout (v1)

**Feature**: 006-user-login-out  
**Date**: 2026-06-03

## New Endpoints

### GET /login

Render login page.

| Condition | Status | Behavior |
|-----------|--------|----------|
| Visitor signed out | 200 | Show login form |
| Visitor already signed in | 200 | No action; login page remains available |

### POST /login

Authenticate submitted credentials.

**Request fields**:
- `email` (required)
- `password` (required)

| Condition | Status | Behavior |
|-----------|--------|----------|
| Valid credentials | 303 | Redirect to authenticated landing/home with success message; create active session |
| Missing/invalid credentials | 200 | Re-render login form with non-sensitive error |
| Repeated rapid failures past threshold | 429 or 200 | Return throttled response/message; no authenticated session |

### POST /logout

Logout authenticated user.

| Condition | Status | Behavior |
|-----------|--------|----------|
| User authenticated | 303 | Logout success and global invalidation of all user sessions |
| User signed out | 401/403 | Block request; no session mutation |

## Protected-Action Session Expiry Contract

For protected actions using Flask-LoginManager:

| Condition | Status | Behavior |
|-----------|--------|----------|
| Session still active | 200 | Proceed normally |
| Session expired | 200 or redirect continuation | Auto-refresh session without re-authentication, then continue protected action |

## Security Contract

- Credential checks use stored Werkzeug password hashes.
- Invalid login responses must not reveal whether email or password was incorrect.
- Logout global invalidation must revoke all session contexts for the user identity.

## Compatibility

- Existing routes remain unchanged unless authentication guard behavior is explicitly added.
- New login/logout routes integrate with existing server-rendered template architecture.
