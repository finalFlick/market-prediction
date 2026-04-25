# Tasks: {{FEATURE_NAME}}

<!--
This template breaks the approved design into discrete, executable
coding tasks. Two-level hierarchy only. Every leaf task ends with a
_Requirements:_ traceability line. Replace placeholders and delete
italic comments before sharing.
-->

## Document Information

- **Feature Name**: {{FEATURE_NAME}}
- **Version**: 0.1
- **Date**: {{DATE}}
- **Author**: {{AUTHOR}}
- **Related Documents**:
  - Requirements: `./requirements.md`
  - Design: `./design.md`

## Implementation Overview

*One short paragraph: the order of attack and why. State which
sequencing strategy you used (foundation-first / feature-slice /
risk-first / hybrid) and why it fits this feature.*

### Strategy

- **Sequencing:** {{foundation-first | feature-slice | risk-first | hybrid}}
- **Testing:** unit + integration written alongside implementation
  (per `coding-standards.mdc`); e2e and backtest smoke at the end.
- **Verification per task:** `pytest -q`, `ruff check .`, `mypy --strict .`
  (per `workflow.mdc`).

### Definition of done for the whole feature

- [ ] Every leaf task below is checked off (`- [x]`).
- [ ] All acceptance criteria from `requirements.md` pass.
- [ ] `pytest`, `ruff`, `mypy` are green.
- [ ] At least one e2e or backtest smoke run exercises the feature.
- [ ] `SESSION_LOG.md` entry recorded.
- [ ] If any architectural decision shifted, `DECISIONS.md` updated.

---

## Implementation Plan

> **Status legend:** `- [ ]` not started · `- [~]` in progress
> · `- [x]` complete

### Phase 1 — Foundation

- [ ] 1. Set up scaffolding for {{FEATURE_NAME}}
- [ ] 1.1 Create module directory and `__init__.py`
  - Add `{{module_path}}/` with empty `__init__.py`.
  - Add `{{module_path}}/errors.py` with module-specific exception
    classes (per `coding-standards.mdc`).
  - Add a stub `{{module_path}}/README.md` describing the module's
    role.
  - _Requirements: 1.1_

- [ ] 1.2 Define typed data contracts
  - Implement pydantic models from `design.md` § Data Models.
  - Add unit tests in `tests/{{module}}/test_models.py` covering
    happy and rejection paths.
  - _Requirements: 1.2, 2.1_

- [ ] 1.3 Wire configuration loading
  - Add a new section to `configs/{{config_file}}.yaml` with the
    keys from `design.md` § Deployment.
  - Implement a pydantic `Config` loader in
    `{{module_path}}/config.py`.
  - Unit tests for missing / malformed config.
  - _Requirements: 3.1_

### Phase 2 — Core implementation

- [ ] 2. Implement {{CORE_COMPONENT}}
- [ ] 2.1 Implement {{Component A}}
  - Create `{{module_path}}/{{component_a}}.py` per `design.md`
    § Components — Component 1.
  - Function signatures come from the design doc; return types are
    typed.
  - Unit tests covering each acceptance criterion.
  - _Requirements: 1.1, 1.2_

- [ ] 2.2 Implement {{Component B}}
  - Create `{{module_path}}/{{component_b}}.py`.
  - Wire `{{Component A}}` as a dependency (no global state).
  - Unit tests including failure modes from `design.md`
    § Error Handling.
  - _Requirements: 2.1, 2.2_

- [ ] 2.3 Add structured logging and metrics
  - Use `monitoring.logger.get_logger(__name__)`; emit the events
    listed in `requirements.md` § Observability.
  - Add gauges / counters per `design.md` § Performance.
  - Tests assert that the documented log events are emitted.
  - _Requirements: 4.1, 4.2_

### Phase 3 — Integration

- [ ] 3. Connect {{FEATURE_NAME}} to the pipeline
- [ ] 3.1 Wire upstream input
  - Read input from `{{upstream_module}}` via its public API.
  - Validate input shape (pandera / pydantic) at the boundary.
  - Integration test using a fixture from `tests/fixtures/`.
  - _Requirements: 1.1, 5.1_

- [ ] 3.2 Wire downstream output
  - Emit typed artifact to `{{downstream_module}}` per
    `design.md` § Data Flow.
  - Idempotency / dedupe key as specified.
  - Integration test covering a full upstream → feature →
    downstream cycle.
  - _Requirements: 5.2_

- [ ] 3.3 Risk path verification (only if feature can produce orders)
  - Ensure every order path calls
    `risk.engine.RiskEngine.check_and_size(...)` (per
    `architecture.mdc` and `security.mdc`).
  - Add a test that asserts a synthetic risk-violating order is
    rejected.
  - _Requirements: 6.1_

### Phase 4 — API / interface layer

*Drop this phase if the feature exposes no external interface.*

- [ ] 4. Expose {{FEATURE_NAME}} via {{REST | CLI | websocket}}
- [ ] 4.1 Implement endpoint / command
  - Per `design.md` § API Design.
  - Input validation; documented error responses.
  - Integration test via FastAPI `TestClient` or `pytest`-driven CLI.
  - _Requirements: 7.1_

- [ ] 4.2 Add OpenAPI / `--help` documentation
  - Auto-generated docstrings; example request/response.
  - _Requirements: 7.2_

### Phase 5 — Verification

- [ ] 5. End-to-end and reproducibility checks
- [ ] 5.1 Backtest / pipeline smoke run
  - Add `tests/e2e/test_{{feature}}.py` that runs a minimal
    end-to-end scenario.
  - For backtest changes: add a deterministic backtest test that
    asserts identical `metrics.json` for a fixed config.
  - _Requirements: 8.1_

- [ ] 5.2 Determinism and seed audit
  - All randomness goes through explicit seeds (per
    `architecture.mdc`).
  - Test asserts byte-identical output across two runs.
  - _Requirements: 8.2_

- [ ] 5.3 Full lint + typecheck + test
  - Run `ruff check .`, `mypy --strict .`, `pytest -q`.
  - Resolve any new findings.
  - _Requirements: all_

### Phase 6 — Documentation and handoff

- [ ] 6. Document and record the feature
- [ ] 6.1 Update operator-facing docs
  - Update `README.md` or `docs/` with how to run / configure the
    feature.
  - Update `AGENTS.md` only if a new agent role is introduced
    (rare).
  - _Requirements: 9.1_

- [ ] 6.2 Record decisions
  - Append a `DECISIONS.md` entry summarizing tradeoffs for any
    decision flagged in `design.md` § Key Design Decisions.
  - Append a `SESSION_LOG.md` entry with date, author, summary,
    spec id.
  - _Requirements: 9.2_

---

## Task Quality Self-Check

Run this before approving Phase 3:

### Completeness

- [ ] Every component in `design.md` has at least one task.
- [ ] Every requirement in `requirements.md` is cited by at least
      one task's `_Requirements:` line.
- [ ] Every leaf task includes a test or testing sub-bullet.

### Scope

- [ ] No task is too big to finish in 1–4 hours.
- [ ] No task is so small it's noise (rename one variable).
- [ ] No task is non-coding ("get user feedback", "deploy").

### Sequencing

- [ ] Tasks are ordered so each builds on completed predecessors.
- [ ] Foundation (models, errors, config) precedes business logic.
- [ ] Business logic precedes integration; integration precedes
      verification.

### Traceability

- [ ] Every leaf task ends with `_Requirements: <ids>_` and the
      ids exist in `requirements.md`.
- [ ] Task IDs (`1.1`, `1.2`, …) are unique and stable.

### Hierarchy

- [ ] No nesting deeper than two levels.
- [ ] Top-level tasks (`1.`, `2.`, …) are phases / epics.
- [ ] Sub-tasks (`1.1`, `1.2`, …) are concrete coding work.

---

> **Execution rules** (per `spec-sessions.mdc` Phase 4):
>
> - Do tasks one at a time unless the user says "run all".
> - Mark `- [~]` when starting a task; `- [x]` only after its tests
>   pass and its acceptance criteria are met.
> - If a task reveals a gap in `requirements.md` or `design.md`,
>   stop and update those documents before continuing.
