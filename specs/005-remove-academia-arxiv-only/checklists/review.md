# PR Review Checklist: Remove Academia.edu — arXiv Only

**Purpose**: Validate requirement quality across all concern areas before PR review  
**Created**: 2026-05-25  
**Feature**: [spec.md](../spec.md) | [plan.md](../plan.md) | [research.md](../research.md)  
**Audience**: Reviewer (PR review gate)  
**Focus**: Route/API contract · Template/UX · Test update requirements · Deletion/cleanup  
**Depth**: Standard

---

## Route / API Contract Requirements Quality

- [ ] CHK001 - Is the "silently ignored" behaviour for the `source` query parameter consistently specified across all three affected routes (`/`, `/api/listings`, `/detail/<id>`), or only described for one route? [Consistency, Spec §FR-003, Contracts §api-contract.md]
- [ ] CHK002 - Is the phrase "MUST NOT accept a `source` parameter" (FR-003) consistent with the acceptance scenario that says the parameter is "silently ignored"? "MUST NOT accept" could imply active rejection; "silently ignored" means passthrough — are these reconciled? [Conflict, Spec §FR-003, §US1 AC-3]
- [ ] CHK003 - Is the removal of the `400 "Missing source parameter."` response from `GET /api/listings` documented as a breaking change in the API contract? [Completeness, Contracts §Removed Behaviour]
- [ ] CHK004 - Are HTTP status codes for all `GET /api/listings` response paths (success: 200, empty: 200, fetch error: 503) explicitly documented in the contract after the change? [Completeness, Contracts §api-contract.md]
- [ ] CHK005 - Are SC-002 (`GET /api/listings` with no params returns arXiv results) and SC-003 (`GET /api/listings?source=academia` returns same arXiv results) independently measurable and non-overlapping? [Measurability, Spec §SC-002, §SC-003]
- [ ] CHK006 - Is the requirement that the `/detail/<id>` cache lookup always uses the `"arxiv"` key explicitly stated in the spec, or only inferred from the data model documentation? [Completeness, data-model.md, Gap in Spec §FR-005]

---

## Template / UX Requirements Quality

- [ ] CHK007 - Is SC-001 ("no source selector/dropdown element") scoped to a specific HTML element or attribute (e.g., absence of `<select id="source">`), or is "element" ambiguous enough to create reviewer disagreement? [Clarity, Spec §SC-001]
- [ ] CHK008 - Are the URL parameter changes for "View details" and "Retry" links (removing `source=` from `url_for` calls) specified as requirements in the spec, or only present in implementation notes in research.md? [Completeness, Research §4, Gap in Spec]
- [ ] CHK009 - Is the heading change from the dynamically capitalised source name to the hardcoded brand name "arXiv" specified anywhere as a requirement or success criterion? [Completeness, Gap — present in Research §4 only]
- [ ] CHK010 - Are requirements defined for which form elements must remain visible after source selector removal (search input field and Fetch Listings button)? [Completeness, Spec §US1, Gap]
- [ ] CHK011 - Is the "Return to list" navigation in `detail.html` covered by a specific acceptance scenario or success criterion, or is it implicitly assumed to work? [Completeness, Gap — US2 covers detail load but not the return link]
- [ ] CHK012 - Is the blank-state UX (home page loaded without having triggered a fetch) defined as a requirement, given the source selector that previously appeared on load is now removed? [Coverage, Edge Case, Gap]

---

## Test Update Requirements Quality

- [ ] CHK013 - Are the specific assertions in `test_discovery_flow.py` that require updating (heading text, request URLs) explicitly listed as requirements, or only implied by the general "all tests must pass" (FR-006)? [Completeness, Spec §FR-006, Gap]
- [ ] CHK014 - Is the expected post-change test count (48 tests) expressed as a measurable success criterion in the spec, or only documented in quickstart.md? [Measurability, Quickstart, Gap in Spec §SC-004]
- [ ] CHK015 - Is the constraint that `test_models.py` (which contains `source="medium"` fixture data) must not be changed explicitly documented as an out-of-scope boundary? [Completeness, Research §5, Gap in Spec]
- [ ] CHK016 - Is FR-007 ("Academia.edu unit test MUST be removed; arXiv unit test MUST remain and pass") sufficient to identify the exact test function name and file path without cross-referencing research.md? [Clarity, Spec §FR-007]
- [ ] CHK017 - Does SC-004 ("all automated tests pass with no new failures introduced; Academia.edu-specific test is absent") remain self-consistent given that a test is intentionally deleted — not failed — making "no new failures" potentially misleading? [Consistency, Spec §SC-004]

---

## Deletion / Cleanup Requirements Quality

- [ ] CHK018 - Is "all Academia.edu client code, imports, and references" (FR-002) scoped to an explicit list of files, or is the removal boundary ambiguous to a reviewer who hasn't read research.md? [Clarity, Spec §FR-002, Research §1]
- [ ] CHK019 - Is the rationale for retaining the `ContentSource` dataclass ("future extensibility") expressed as a verifiable requirement with an acceptance criterion, or only as unverifiable design intent? [Measurability, Spec §FR-009]
- [ ] CHK020 - Are the requirements for removing `CONTENT_SOURCES` (Spec §FR-009) and the data model documentation (data-model.md §CONTENT_SOURCES) consistent in describing what is removed and what is retained? [Consistency, Spec §FR-009, data-model.md]
- [ ] CHK021 - Is it specified whether the `selected_source` variable and the `sources` key in the template context dict should also be removed, or only that the selector HTML element must be absent from the page? [Clarity, Research §6, Gap in Spec §FR-001]
- [ ] CHK022 - Is the stale `"academia"` key in `LATEST_RESULTS` (populated from a prior app session before this change) addressed with a measurable removal criterion, or only described informally in the edge cases section? [Coverage, Edge Cases, Spec]

---

## Scenario Coverage

- [ ] CHK023 - Are requirements defined for each of the three route simplifications independently (`/`, `/api/listings`, `/detail/<id>`), or are their individual behaviours only described collectively under US1? [Coverage, Spec §FR-003, §FR-004, §FR-005]
- [ ] CHK024 - Is a requirement or acceptance scenario defined for the case where a user navigates to `/detail/<id>` without having fetched results first (empty arXiv cache)? [Coverage, Edge Case, Gap]
- [ ] CHK025 - Is the scope of "no reference to Academia.edu appears" (SC-001) limited to the home page only, or does it apply to all rendered routes (detail page, registration pages, navigation)? [Clarity, Spec §SC-001]
