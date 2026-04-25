# FEATURE-0022: Paper Broker and Broker Registry

## Parent Epic

risk-execution-safety

## Status

Proposed

## Summary

Define paper execution as the default broker path and keep live adapters gated until evidence is complete.

## Why

Paper trading gives operational evidence without live capital, while premature live registration is unsafe.

## What

A broker capability for PaperBroker behavior, adapter registry policy, live registration rejection, and phase-specific broker support.

## User / System Story

As a platform operator or implementation agent,
I want paper broker and broker registry,
so that the trading-lab platform can satisfy the related requirements with evidence.

## Source Traceability

- requirements.md: Req 4, 25, 43
- design.md: Component 8; LiveBrokerRegistry; Paper Trading Simulator; MVP-0 Acceptance
- Repo conventions: .cursor/rules/architecture.mdc, .cursor/rules/security.mdc, .cursor/rules/workflow.mdc, .cursor/rules/spec-sessions.mdc, and AGENTS.md.

## Requirements Covered

- Req 4
- Req 25
- Req 43

## Design Alignment

Component 8; LiveBrokerRegistry; Paper Trading Simulator; MVP-0 Acceptance. This feature states the expected capability and review evidence without prescribing code-level implementation details beyond the design and project rules.

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

- live registration forbidden tests; paper broker scenarios; config gate checks
- Stage-appropriate unit, integration, contract, e2e, safety, or smoke tests.
- Final implementation evidence should include pytest -q, ruff check ., and mypy --strict . unless the approved task narrows verification with a documented reason.

## Dependencies

- risk path; cost model; execution config

## Risks / Edge Cases

- Live adapter stubs can accidentally become callable.
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
- Added `LiveBrokerRegistry` and `LiveAdapterRegistrationForbidden` in `execution/brokers/registry.py`.
- Added `configs/runtime.yaml` with `live_adapters_unlocked: false` default lock.
- Added `BinanceLive` and `CoinbaseLive` aliases for design naming parity.
- Updated `execution/runner.py` to register `paper` by default and refuse locked live brokers at CLI startup.

Tests:
- `py -3.12 -m pytest -q tests/security/test_live_registration_forbidden.py` -> 5 passed
- `py -3.12 -m pytest -q tests/security/` -> 21 passed

Files changed:
- `execution/brokers/registry.py`
- `execution/brokers/binance.py`
- `execution/brokers/coinbase.py`
- `execution/runner.py`
- `configs/runtime.yaml`
- `tests/security/test_live_registration_forbidden.py`

Design notes:
- MVP-0 lock behavior matches `requirements.md` Req 4.6 and `design.md` Component 8 (`LiveBrokerRegistry` refuse-until-unlocked contract).

Known follow-ups:
- Add paper/live parity checks per broker capability matrix.
- Migrate unlock source from `configs/runtime.yaml` to `config_kv` once v1.1 pre-live gate work lands.
- Implement full live gate condition checks and ceremony for `live_adapters_unlocked`.
