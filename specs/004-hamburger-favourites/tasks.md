# Tasks: Hamburger Menu with Favourites

**Input**: Design documents from `/specs/004-hamburger-favourites/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

---

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Ensure Python 3.x, Flask, and all dependencies installed per requirements.txt
- [X] T002 [P] Confirm `src/`, `templates/`, `static/`, and `tests/` directories exist

---

## Phase 2: Foundational (Blocking Prerequisites)

- [X] T003 Add `FAVOURITES_STORE` and session secret key to src/app.py
- [X] T004 [P] Add `user_id` session logic to src/app.py
- [X] T005 [P] Create new template file src/templates/favourites.html

---

## Phase 3: User Story 1 - Save a Paper to Favourites (Priority: P1) 🎯 MVP

**Goal**: User can save/remove a paper as a favourite from the detail page using the heart button.
**Independent Test**: Visit detail page, click heart, confirm state toggles and paper appears/vanishes from favourites.

- [X] T006 [P] [US1] Add heart button form to src/templates/detail.html
- [X] T007 [US1] Implement POST /favourite/toggle route in src/app.py
- [X] T008 [US1] Update item_detail route in src/app.py to pass is_favourite to template
- [X] T009 [US1] Update detail.html to render heart filled/unfilled based on is_favourite
- [X] T010 [US1] Add logic to toggle paper in FAVOURITES_STORE in src/app.py
- [X] T011 [US1] Add/extend integration tests for heart toggle in tests/integration/test_discovery_flow.py

---

## Phase 4: User Story 2 - Access Favourites via Hamburger Menu (Priority: P2)

**Goal**: User can access a Favourites page via a hamburger menu on all pages, see saved papers, and remove them.
**Independent Test**: Save a paper, open hamburger, go to Favourites, see paper listed, remove it, confirm gone.

- [X] T012 [P] [US2] Add hamburger menu markup to src/templates/base.html
- [X] T013 [US2] Add hamburger menu CSS to src/static/styles.css
- [X] T014 [US2] Implement GET /favourites route in src/app.py
- [X] T015 [US2] Render saved papers in src/templates/favourites.html
- [X] T016 [US2] Add × remove button/form to favourites.html
- [X] T017 [US2] Implement POST /favourite/remove route in src/app.py
- [X] T018 [US2] Add/extend integration tests for Favourites page and remove in tests/integration/test_discovery_flow.py

---

## Phase 5: Polish & Cross-Cutting Concerns

- [X] T019 [P] Polish heart and hamburger styles in src/static/styles.css
- [X] T020 [P] Add empty state message to favourites.html
- [X] T021 [P] Update quickstart.md with new usage instructions
- [X] T022 [P] Review and update documentation in specs/004-hamburger-favourites/
- [X] T023 [P] Final code cleanup and ensure all tests pass

---

## Dependencies & Execution Order

- Phase 1 must complete before Phase 2
- Phase 2 must complete before any user story work
- User Story 1 (P1) is MVP and can be delivered independently
- User Story 2 (P2) depends on US1 for saved papers, but can be implemented in parallel after foundational phase
- Polish phase can run in parallel after all user stories are complete

---

## Parallel Execution Examples

- T002, T004, T005 can be done in parallel
- T006, T011 can be done in parallel with T012, T013, T018
- T019–T023 can be done in parallel after user stories

---

## MVP Scope

- Complete through T011 (User Story 1) for a minimal, testable MVP

---

## Format Validation

All tasks follow the strict checklist format: `- [ ] TXXX [P?] [US?] Description with file path`
