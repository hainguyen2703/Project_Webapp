# API Contract: Paper Discovery Web App (v3 — Favourites)

**Feature**: 004-hamburger-favourites  
**Date**: 2026-05-26  
**Extends**: `specs/003-arxiv-only-source/contracts/api-contract.md`  
**Changes**: Three new endpoints added. All existing endpoints unchanged.

---

## New Endpoints

### POST /favourite/toggle

Toggle the favourite state of a paper for the current user session. Adds the paper if not currently favourited; removes it if already favourited.

**Request body** (form-encoded):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `item_id` | `string` | Yes | The paper's arXiv ID (full URL, e.g., `http://arxiv.org/abs/1234.5678v1`) |

**Behaviour**:

| Condition | Action | Redirect |
|-----------|--------|----------|
| Paper not in favourites; found in `LATEST_RESULTS["arxiv"]` | Add to `FAVOURITES_STORE[user_id]` (prepend) | `303 → GET /detail/{item_id}` |
| Paper already in favourites | Remove from `FAVOURITES_STORE[user_id]` | `303 → GET /detail/{item_id}` |
| `item_id` missing from request | No action | `303 → GET /` |

**Side effects**: Creates `session['user_id']` (UUID) on first call if not already set.

---

### POST /favourite/remove

Remove a specific paper from the user's favourites. Intended for use from the Favourites page × button.

**Request body** (form-encoded):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `item_id` | `string` | Yes | The paper's arXiv ID to remove |

**Behaviour**:

| Condition | Action | Redirect |
|-----------|--------|----------|
| Paper in favourites | Remove from `FAVOURITES_STORE[user_id]` | `303 → GET /favourites` |
| Paper not in favourites | No action (idempotent) | `303 → GET /favourites` |
| `item_id` missing | No action | `303 → GET /favourites` |

---

### GET /favourites

Render the Favourites page listing all saved papers for the current user session.

**Query parameters**: None

**Response**:

| Condition | HTTP Status | Rendered content |
|-----------|-------------|-----------------|
| User has saved papers | 200 | Favourites page with paper list (most recently saved first) |
| User has no saved papers | 200 | Favourites page with "No favourites saved yet" empty state |

**Page content** (per paper entry):
- Paper title (link to `GET /detail/{item_id}`)
- Authors
- Published date
- × remove form (POST to `/favourite/remove`)

---

## Updated Endpoints

### GET /detail/{item_id} *(extended)*

Previously only looked up papers from `LATEST_RESULTS["arxiv"]`. Now falls back to `FAVOURITES_STORE[user_id]` if not found there.

**Updated response table**:

| Condition | HTTP Status |
|-----------|-------------|
| Paper found in `LATEST_RESULTS["arxiv"]` | 200 |
| Paper not in `LATEST_RESULTS` but found in `FAVOURITES_STORE[user_id]` | 200 |
| Paper not found in either | 404 |

**New context variable passed to template**:

| Variable | Type | Description |
|----------|------|-------------|
| `is_favourite` | `bool` | `True` if paper is currently in `FAVOURITES_STORE[user_id]` |

---

## Unchanged Endpoints

| Endpoint | Status |
|----------|--------|
| `GET /` | Unchanged |
| `GET /api/listings` | Unchanged |
