# Quickstart: UI Guest & Registration Navigation

**Feature**: `003-ui-guest-registration-nav`  
**Date**: 2026-05-15

---

## What This Feature Does

Adds a hamburger menu (☰ Menu) to the site header, visible on every page. Clicking it opens a dropdown containing a "Register" link that navigates the user to `/register`. No features are gated; guests can use the site as before.

---

## Files Changed

| File | Change |
|---|---|
| `src/templates/base.html` | Header wrapped in flex row; hamburger button + dropdown nav added; inline `<script>` at end of body |
| `src/static/styles.css` | `.nav-dropdown` and related rules added |

---

## Running the App

```powershell
# From repo root with virtualenv active
python -m flask --app src.app run --debug
```

Open `http://127.0.0.1:5000/` in a browser.

---

## Manual Acceptance Tests

Run these in a browser to verify the feature works correctly:

### AC-1: Hamburger trigger visible on every page

1. Open `http://127.0.0.1:5000/`
2. Confirm the header shows **☰ Menu** button in the top-right area
3. Navigate to `http://127.0.0.1:5000/register`
4. Confirm the same **☰ Menu** button is present

**Expected**: ☰ Menu appears in the header on both pages.

### AC-2: Dropdown opens and closes on click

1. Open `http://127.0.0.1:5000/`
2. Click **☰ Menu**
3. Confirm a dropdown panel appears containing a **Register** link
4. Click **☰ Menu** again
5. Confirm the dropdown closes

**Expected**: Dropdown toggles open/closed on each click. Dropdown does NOT open or close on hover.

### AC-3: Register link navigates to registration page

1. Click **☰ Menu** to open the dropdown
2. Click **Register** inside the dropdown
3. Confirm you land on the registration page at `/register`

**Expected**: Browser navigates to `http://127.0.0.1:5000/register`.

### AC-4: Click-outside closes dropdown

1. Click **☰ Menu** to open the dropdown
2. Click anywhere on the page outside the dropdown
3. Confirm the dropdown closes

**Expected**: Dropdown closes. No page navigation occurs.

### AC-5: No layout shift

1. Open `http://127.0.0.1:5000/`
2. Confirm the **Paper Discovery** heading and subtitle paragraph are fully visible and not pushed or shifted by the hamburger button
3. Open the dropdown
4. Confirm the dropdown overlays content without moving any element

**Expected**: Opening/closing the dropdown causes no layout reflow.

### AC-6: Existing features accessible (regression)

1. Open `http://127.0.0.1:5000/`
2. Select a source and run a discovery query
3. Confirm results load normally

**Expected**: All previously working features behave identically.

---

## Automated Tests

```powershell
# From repo root with virtualenv active
pytest tests/ -v
```

All 38 existing tests MUST pass. New tests covering the navigation dropdown are in `tests/integration/test_nav_dropdown.py`.
