# Implementation Plan: UI Guest & Registration Navigation

**Branch**: `003-ui-guest-registration-nav` | **Date**: 2026-05-15 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/003-ui-guest-registration-nav/spec.md`

## Summary

Add a hamburger menu (☰ Menu) to the site header, visible on every page via `base.html`. Clicking the trigger opens a dropdown containing a single "Register" link pointing to `/register`. Implemented as a pure Jinja2/CSS/vanilla-JS change with no new routes, models, or server-side logic. All existing features remain available to guests without any registration prompt.

## Technical Context

**Language/Version**: Python 3.12.13  
**Primary Dependencies**: Flask≥2.0, Jinja2 (bundled), CSS (vanilla), JavaScript (vanilla inline)  
**Storage**: N/A — no new data models  
**Testing**: pytest≥8.0 + Flask test client  
**Target Platform**: Desktop browser, Flask server-rendered HTML  
**Project Type**: Web application (server-rendered, single-package Flask)  
**Performance Goals**: Zero additional HTTP requests; pure CSS/JS toggle — no latency impact  
**Constraints**: Must not break any existing route, template, or test; no external JS/CSS libraries  
**Scale/Scope**: 1 template file (`base.html`), 1 CSS file (`styles.css`), 1 new test file

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Evaluation | Status |
|---|---|---|
| I. Code Quality & Maintainability | Change confined to `base.html` + `styles.css`; vanilla JS IIFE in `<script>` at end of body; no new modules added | **PASS** |
| II. User Experience Consistency | Dropdown uses existing colour palette (`#2563eb`, `#ffffff`, `#f4f6f8`, `#1f2937`), `border-radius: 12px`, `box-shadow` matching existing panels; no regression on existing journeys | **PASS** |
| III. Performance Requirements | No new server requests; JS + CSS are inline/near-zero bytes; no rendering impact on existing content | **PASS** |

Post-design re-evaluation: No violations introduced. Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/003-ui-guest-registration-nav/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output
├── spec.md              # Feature spec
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

> Note: No `data-model.md` or `contracts/` — this feature introduces no new entities or external interfaces.

### Source Code

```text
src/
├── templates/
│   └── base.html        # MODIFIED: flex header wrapper, hamburger button, dropdown nav, inline script
└── static/
    └── styles.css       # MODIFIED: nav-dropdown styles, header flex layout

tests/
└── integration/
    └── test_nav_dropdown.py   # NEW: dropdown HTML structure tests
```

**Structure Decision**: Single-package Flask web application. Only template and CSS files are changed; no new source modules. A single new integration test file covers the HTML assertions.
