# Research: UI Guest & Registration Navigation

**Feature**: `003-ui-guest-registration-nav`  
**Phase**: 0  
**Date**: 2026-05-15

---

## RQ-001 — Dropdown Implementation Pattern

**Decision**: Click-triggered `<button id="menu-trigger">` with sibling `<nav id="menu-dropdown">` toggled via a `.open` CSS class.

**Rationale**: Native `<button>` is keyboard-accessible by default (Enter/Space). A CSS class toggle keeps state out of inline styles, making the hidden-by-default initial state testable via regex on rendered HTML. The `display: none` / `.open { display: block }` pattern is universally supported with no library dependency.

**Alternatives considered**:
- CSS-only `:hover` trigger — rejected per FR-004 (hover MUST NOT trigger the dropdown).
- `<details>/<summary>` native disclosure widget — rejected because it renders as an indented block and cannot be freely positioned without overriding all UA styles.
- Checkbox hack (`:checked` + label) — rejected; more complex than needed and requires a hidden input.

---

## RQ-002 — Layout Without Layout Shift

**Decision**: `position: relative` on `<header>`, `position: absolute; top: 100%; right: 0` on `#menu-dropdown`.

**Rationale**: Absolute positioning removes the dropdown from document flow; the header layout (h1 + subtitle paragraph) is entirely unaffected. `right: 0` aligns the dropdown to the right edge of the header, which is the natural right side of the page content column (`max-width: 1080px; margin: 0 auto`). `z-index: 100` clears all existing page content (the existing app has no high z-index declarations).

**Trigger layout**: Wrapping the `<h1>`/`<p>` pair and the `<button>` in a `<div style="display: flex; justify-content: space-between; align-items: flex-start;">` achieves side-by-side layout without touching existing media queries.

---

## RQ-003 — Minimal Vanilla JS (Toggle + Click-Outside)

**Decision**: IIFE with two event listeners — one on the trigger (toggle + `stopPropagation`), one on `document` (click-outside close). Placed in an inline `<script>` at the end of `<body>`.

```js
(function () {
  var trigger = document.getElementById('menu-trigger');
  var dropdown = document.getElementById('menu-dropdown');
  trigger.addEventListener('click', function (e) {
    e.stopPropagation();
    var isOpen = dropdown.classList.toggle('open');
    trigger.setAttribute('aria-expanded', isOpen);
  });
  document.addEventListener('click', function (e) {
    if (!dropdown.contains(e.target) && e.target !== trigger) {
      dropdown.classList.remove('open');
      trigger.setAttribute('aria-expanded', 'false');
    }
  });
}());
```

**Rationale**: `stopPropagation` prevents the same click from immediately triggering the document listener and closing the dropdown. The `contains` check covers clicks on the "Register" link and any future items added inside the dropdown. ARIA `aria-expanded` is kept in sync to satisfy screen-reader state announcement.

**Alternatives considered**: Arrow functions + `const` — rejected to retain compatibility with older desktop browsers that may be used in the target environment; `var` + regular `function` is universally safe.

---

## RQ-004 — Hamburger Icon (☰) Accessibility

**Decision**: Use `☰` (U+2630, Unicode Trigram for Heaven) with adjacent visible text `Menu` inside the `<button>`. ARIA label on the button is `"Menu"`.

**Rationale**: The character has full support in all modern browsers and degrades gracefully (falls back to a box glyph on very old browsers, but the visible text "Menu" remains). Screen readers will read the `aria-label="Menu"` text, not the glyph. Pairing with visible "Menu" text makes intent clear to sighted users without requiring CSS-drawn icons (3-line CSS icon requires pseudo-elements and is harder to maintain).

**Alternatives considered**: SVG icon — rejected as unnecessary complexity for a single glyph. CSS `::before`/`::after` icon — same rejection. Icon library (FontAwesome etc.) — rejected as an external dependency.

---

## RQ-005 — Integration Testing Strategy

**Decision**: Flask test client HTML string assertions + `re.search` for dropdown structure verification. No Selenium or browser required.

**Rationale**: This feature has no new server-side logic; all changes are in the Jinja2 template and CSS. The Flask test client renders Jinja2 → checking the HTML string directly is both sufficient and fast. CSS visibility state (`.open` class absent by default) is verifiable from the initial HTML. JS toggle behaviour is intentionally excluded from server-side tests (it is client-side only) but covered by the acceptance test script in `quickstart.md`.

**Test targets**:
1. `id="menu-trigger"` present in HTML of every route.
2. `aria-expanded="false"` on initial render.
3. `id="menu-dropdown"` present with no `open` class on initial render.
4. `href="/register"` inside `#menu-dropdown`.
5. All previously-accessible routes return HTTP 200 (regression guard).
