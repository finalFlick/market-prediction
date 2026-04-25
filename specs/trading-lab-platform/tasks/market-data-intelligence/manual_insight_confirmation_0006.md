# FEATURE-0006: Manual Insight Intake and Source Confirmation

## Parent Epic

market-data-intelligence

## Status

Proposed

## Summary

Define how pasted text, URLs, and external observations become structured insight-only records with confirmation tiers.

## Why

Manual and LLM-assisted research can add context but must not become unverified trade execution.

## What

An intake capability for insight records, provenance, confirmation policy, and trade_allowed=false boundaries.

## User / System Story

As a platform operator or implementation agent,
I want manual insight intake and source confirmation,
so that the trading-lab platform can satisfy the related requirements with evidence.

## Source Traceability

- requirements.md: Req 9, 18, 20, 23
- design.md: Component 5 Insight Intake; Source Confirmation Policy; LLM isolation
- Repo conventions: .cursor/rules/architecture.mdc, .cursor/rules/security.mdc, .cursor/rules/workflow.mdc, .cursor/rules/spec-sessions.mdc, and AGENTS.md.

## Requirements Covered

- Req 9
- Req 18
- Req 20
- Req 23

## Design Alignment

Component 5 Insight Intake; Source Confirmation Policy; LLM isolation. This feature states the expected capability and review evidence without prescribing code-level implementation details beyond the design and project rules.

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

- schema validation tests; trade_allowed boundary tests; provenance checks
- Stage-appropriate unit, integration, contract, e2e, safety, or smoke tests.
- Final implementation evidence should include pytest -q, ruff check ., and mypy --strict . unless the approved task narrows verification with a documented reason.

## Dependencies

- run memory; LLM provider; audit log

## Risks / Edge Cases

- Insight text can smuggle symbol/side/size recommendations.
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
