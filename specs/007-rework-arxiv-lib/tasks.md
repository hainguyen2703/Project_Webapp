# Tasks: Standardize arXiv Discovery Source

**Input**: Design documents from /specs/007-rework-arxiv-lib/  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: No explicit test-first or TDD request appears in the specification, so dedicated test tasks are omitted.

**Organization**: Tasks are grouped by user story to keep each story independently implementable and verifiable.

## Format: [ID] [P?] [Story] Description

- [P]: Can run in parallel (different files, no blocking dependency)
- [Story]: User story label for story-phase tasks only
- Every task includes an explicit file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare dependency and baseline migration context for arXiv library adoption.

- [X] T001 Add Python arXiv library dependency to requirements in requirements.txt
- [X] T002 Prepare arXiv client module for library-based implementation in src/clients/arxiv_client.py
- [X] T003 Document setup changes for arXiv library migration in specs/007-rework-arxiv-lib/quickstart.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build shared normalization, validation, and outcome plumbing used by all user stories.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Implement canonical arXiv ID parsing helper in src/clients/arxiv_client.py
- [X] T005 [P] Implement required-field validation helper for discovery records in src/services/discovery_service.py
- [X] T006 [P] Tighten article-level required-field and timestamp validation in src/models/article.py
- [X] T007 Implement normalized success/empty/error outcome assembly in src/services/discovery_service.py
- [X] T008 [P] Align fetched_at and payload-shape behavior for empty/error outcomes in src/services/result_formatter.py
- [X] T009 Define timeout and non-technical error message constants in src/services/discovery_service.py

**Checkpoint**: Foundation complete; user stories can proceed.

---

## Phase 3: User Story 1 - Discover papers with consistent metadata (Priority: P1) MVP

**Goal**: Return consistent discovery results using the arXiv Python library with canonical metadata fields.

**Independent Test**: Run representative searches and confirm each result includes title, authors, summary, publication date, canonical arXiv ID, and canonical link in a stable format.

### Implementation for User Story 1

- [X] T010 [US1] Replace manual XML fetch flow with arXiv library query execution in src/clients/arxiv_client.py
- [X] T011 [US1] Map arXiv library results to normalized PaperArticle records in src/clients/arxiv_client.py
- [X] T012 [US1] Update discovery fetch pipeline to consume normalized client records in src/services/discovery_service.py
- [X] T013 [P] [US1] Preserve source=arxiv request and result status wiring in src/app.py
- [X] T014 [P] [US1] Render stable metadata fields for each discovery result in src/templates/home.html
- [X] T015 [US1] Preserve favorites toggle eligibility with canonical arXiv IDs in src/app.py

**Checkpoint**: User Story 1 is independently functional and demonstrable.

---

## Phase 4: User Story 2 - Open paper details without missing information (Priority: P2)

**Goal**: Ensure detail pages show complete required content and graceful handling of missing optional fields.

**Independent Test**: Open multiple detail pages from discovery results and verify required fields are always present while missing optional fields are clearly indicated.

### Implementation for User Story 2

- [X] T016 [US2] Resolve detail lookup consistently by canonical arXiv ID in src/app.py
- [X] T017 [US2] Render required detail content and canonical identifier on detail page in src/templates/detail.html
- [X] T018 [US2] Build detail-view context fallbacks for missing optional metadata in src/app.py
- [X] T019 [P] [US2] Display unavailable-state text for missing optional fields in src/templates/detail.html
- [X] T020 [US2] Ensure discovery-detail metadata parity through article serialization behavior in src/models/article.py

**Checkpoint**: User Story 2 is independently functional without requiring User Story 3.

---

## Phase 5: User Story 3 - Receive graceful behavior during source disruption (Priority: P3)

**Goal**: Provide timeout-aware retry behavior and resilient partial-success handling during source problems.

**Independent Test**: Simulate timeout and malformed-record scenarios and verify retry-ready error states appear within 4 seconds while valid records still render when available.

### Implementation for User Story 3

- [X] T021 [US3] Enforce 4-second timeout for arXiv retrieval requests in src/clients/arxiv_client.py
- [X] T022 [US3] Map timeout and upstream failures to retry-ready error outcomes in src/services/discovery_service.py
- [X] T023 [US3] Exclude malformed required-field records while retaining valid records in src/services/discovery_service.py
- [X] T024 [P] [US3] Render retry-focused timeout and failure states on home page in src/templates/home.html
- [X] T025 [P] [US3] Align API error response mapping for discovery source failures in src/app.py
- [X] T026 [US3] Preserve partial-success behavior when some records are filtered out in src/services/discovery_service.py

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, documentation alignment, and rollout readiness across all stories.

- [X] T027 [P] Update validation scenarios and execution notes in specs/007-rework-arxiv-lib/quickstart.md
- [X] T028 [P] Align contract examples with implemented identifier/timeout behavior in specs/007-rework-arxiv-lib/contracts/api-contract.md
- [X] T029 [P] Record implementation decisions and residual risks in specs/007-rework-arxiv-lib/research.md
- [X] T030 Capture final implementation and verification notes in specs/007-rework-arxiv-lib/plan.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies.
- Foundational (Phase 2): Depends on Setup completion and blocks all user story work.
- User Story phases (Phases 3-5): Depend on Foundational completion.
- Polish (Phase 6): Depends on completion of all desired user stories.

### User Story Dependencies

- User Story 1 (P1): Starts after Foundational and has no dependency on other stories.
- User Story 2 (P2): Starts after Foundational; uses canonical records produced by US1 pipeline but remains independently testable.
- User Story 3 (P3): Starts after Foundational; can be implemented independently of US2 and focuses on disruption behavior.

### Within Each User Story

- Service/client behavior before route/template integration.
- Route/context wiring before final rendering changes.
- Story behavior complete before cross-cutting polish updates.

---

## Parallel Opportunities

- Phase 2: T005, T006, and T008 can run in parallel.
- US1: T013 and T014 can run in parallel after T010-T012 begin.
- US2: T018 and T019 can run in parallel.
- US3: T024 and T025 can run in parallel with T022/T023.
- Polish: T027, T028, and T029 can run in parallel.

---

## Parallel Example: User Story 1

```bash
Task: T013 [US1] Preserve source=arxiv request and result status wiring in src/app.py
Task: T014 [US1] Render stable metadata fields for each discovery result in src/templates/home.html
```

## Parallel Example: User Story 2

```bash
Task: T018 [US2] Build detail-view context fallbacks for missing optional metadata in src/app.py
Task: T019 [US2] Display unavailable-state text for missing optional fields in src/templates/detail.html
```

## Parallel Example: User Story 3

```bash
Task: T024 [US3] Render retry-focused timeout and failure states on home page in src/templates/home.html
Task: T025 [US3] Align API error response mapping for discovery source failures in src/app.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independently before expanding scope.

### Incremental Delivery

1. Deliver US1 for canonical discovery output.
2. Deliver US2 for detail completeness guarantees.
3. Deliver US3 for disruption resilience and retry behavior.
4. Complete Phase 6 for documentation and final alignment.

### Parallel Team Strategy

1. Team completes Setup and Foundational phases together.
2. After Foundation:
   - Developer A: US1
   - Developer B: US2
   - Developer C: US3
3. Rejoin for Polish tasks and final validation capture.

