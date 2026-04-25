# FEATURE-0021: Non-Bypassable Risk Path

## Parent Epic

risk-execution-safety

## Status

Proposed

## Summary

Define the single valid path from strategy targets to broker placement and the evidence that no bypass exists.

## Why

Risk is the hard safety boundary for every order, paper or live.

## What

A risk-path capability covering target positions, RiskEngine.check_and_size, rejection handling, and forbidden direct broker calls.

## User / System Story

As a platform operator or implementation agent,
I want non-bypassable risk path,
so that the trading-lab platform can satisfy the related requirements with evidence.

## Source Traceability

- requirements.md: Req 20, 23, 24, 25
- design.md: Component 7; immutable pipeline order; Risk Management Design; Security Considerations
- Repo conventions: .cursor/rules/architecture.mdc, .cursor/rules/security.mdc, .cursor/rules/workflow.mdc, .cursor/rules/spec-sessions.mdc, and AGENTS.md.

## Requirements Covered

- Req 20
- Req 23
- Req 24
- Req 25

## Design Alignment

Component 7; immutable pipeline order; Risk Management Design; Security Considerations. This feature states the expected capability and review evidence without prescribing code-level implementation details beyond the design and project rules.

## In Scope

- The behavior, outcome, or platform capability described above.
- Traceability to listed requirements and design sections.
- Validation expectations appropriate to the affected pipeline stage.
- Documentation and diagnostics needed for review and operation.

## Out of Scope

- Implementation code.
- Exact file-level steps unless already mandated by design.md.
- Later-phase capabilities not listed in the source traceability.
- Any change that bypasses risk, weakens LLM isolation, or breaks the one-way pipeline.

## Acceptance Criteria

- Given the source documents and repo standards, when an implementation plan is prepared, then it traces this feature to the listed requirements and design sections.
- Given the feature is implemented, when validation runs, then the expected tests and checks listed below pass with command/result evidence.
- Given unsupported or later-phase behavior is requested, when the system handles it, then it rejects, defers, or marks it explicitly rather than silently enabling it.

## Validation Expectations

- risk accept/reject tests; import graph tests; bypass flag/static checks
- Stage-appropriate unit, integration, contract, e2e, safety, or smoke tests.
- Final implementation evidence should include pytest -q, ruff check ., and mypy --strict . unless the approved task narrows verification with a documented reason.

## Dependencies

- strategy framework; broker interface; security tests

## Risks / Edge Cases

- Convenience APIs can create hidden order paths.
- Phase boundaries must remain visible in implementation and docs.
- Reviewers must confirm validation evidence is real, not aspirational.

## Observability / Diagnostics

The implementation should expose enough logs, metrics, audit records, UI state, or artifact metadata for an operator or reviewer to determine whether the feature is active, healthy, degraded, rejected, or deferred. Diagnostics must avoid logging secrets and preserve the auditability expectations in design.md.

## Documentation Expectations

- Update operator or developer documentation when the feature changes a workflow, command, route, config surface, or safety policy.
- Update DECISIONS.md if implementation changes architecture, risk posture, phase scope, or release gates.
- Update SESSION_LOG.md with verification evidence when implementation work lands.

## Done Means

- [ ] The feature outcome is implemented or explicitly marked as deferred according to its phase.
- [ ] Acceptance criteria above are satisfied with evidence.
- [ ] Validation expectations are covered by tests, smoke checks, or documented manual verification.
- [ ] Source traceability remains accurate after implementation.
- [ ] Required docs, decisions, and session log entries are updated.

## Resolution

Status: Partial

Implemented:
- Added an explicit broker-registration gate that refuses live adapters by default, reducing accidental non-governed execution paths.
- Added security tests proving locked live adapters are rejected while paper registration stays available.
- Updated runner startup flow to enforce the registration gate before strategy execution starts.

Tests:
- `py -3.12 -m pytest -q tests/security/test_live_registration_forbidden.py` -> 5 passed
- `py -3.12 -m pytest -q tests/security/` -> 21 passed

Files changed:
- `execution/brokers/registry.py`
- `execution/runner.py`
- `tests/security/test_live_registration_forbidden.py`

Design notes:
- This is a partial contribution to the non-bypassable path objective by hardening broker registration; it does not replace the required `risk.engine.RiskEngine.check_and_size` path.

Known follow-ups:
- Add explicit tests asserting all order placement still routes through `RiskEngine.check_and_size`.
- Add static/import-graph checks that no alternative order path can be introduced via future execution modules.
