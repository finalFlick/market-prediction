# Epic: Backend API and Streaming

## Status

Proposed

## Summary

Expose run, strategy, configuration, audit, and command capabilities through typed APIs and realtime event streams.

## Why This Matters

This epic supports the platform goal of learning to make money over time while preserving deterministic evidence, non-bypassable risk, and operator trust. It groups work that should be planned and reviewed as one platform capability.

## Goals

- Represent the relevant requirements as reviewable feature tickets.
- Preserve the architecture and safety boundaries in design.md.
- Make validation expectations visible before implementation starts.

## Non-Goals

- Write implementation code.
- Replace requirements.md or design.md as the source of truth.
- Weaken the one-way pipeline, LLM isolation, or risk gate.

## Scope

### Included

- Feature tickets listed below.
- Traceability to requirements and design sections.
- Risks, dependencies, acceptance criteria, and validation expectations.

### Excluded

- Implementation file plans not already required by the design.
- Live-capital promotion unless explicitly covered by a gated feature.
- New trading-signal hypotheses, which follow the SIGNALS.md research workflow.

## Source Traceability

- requirements.md: Req 10, 17, 33, 35, 36, 41
- design.md: Components 19, 20, API Design, Event Schemas, Error Handling
- Repo standards: .cursor/rules/architecture.mdc, .cursor/rules/security.mdc, .cursor/rules/workflow.mdc, .cursor/rules/spec-sessions.mdc, and AGENTS.md.

## Features

- [ ] [FEATURE-0028 - Run, Strategy, and Config API Surfaces](./run_strategy_config_api_0028.md)
- [ ] [FEATURE-0029 - Asynchronous Mutating Command Pattern](./async_mutating_command_pattern_0029.md)
- [ ] [FEATURE-0030 - Realtime Run Event Streaming](./realtime_run_event_streaming_0030.md)

## Dependencies

- Approved requirements.md and design.md.
- Existing repo architecture and package boundaries.
- Verification workflow from .cursor/rules/workflow.mdc.

## Risks and Constraints

- Scope can drift if later-phase items are treated as MVP-0 blockers.
- Tickets must remain product/spec artifacts rather than disguised implementation checklists.
- Any order-producing capability must preserve Strategy.target_positions -> RiskEngine.check_and_size -> Broker.place_order.

## Acceptance Criteria

- Every feature in this epic has a parent epic, source traceability, acceptance criteria, validation expectations, dependencies, risks, observability, documentation, and done criteria.
- The epic can be used to sequence implementation without requiring code-level prescriptions.
- The epic does not contradict requirements.md, design.md, or Cursor rules.

## Validation Expectations

- Review links and paths in this epic and its feature tickets.
- Use ReadLints for edited Markdown.
- During implementation, run the relevant tests plus pytest -q, ruff check ., and mypy --strict . unless a task-specific waiver is recorded.

## Notes

Implementation agents should pick feature tickets rather than this epic directly. If implementation reveals a gap in requirements or design, update those source documents before changing code.
