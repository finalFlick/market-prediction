# Epic: Frontend Operator Experience

## Status

Proposed

## Summary

Give a single operator a beginner-safe dashboard for runs, strategy evidence, configuration, learning, alerts, and diagnostics.

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

- requirements.md: Req 33, 34, 35, 36, 44, 45, 50
- design.md: Component 21, Frontend Page Inventory, Component Library, Performance Considerations
- Repo standards: .cursor/rules/architecture.mdc, .cursor/rules/security.mdc, .cursor/rules/workflow.mdc, .cursor/rules/spec-sessions.mdc, and AGENTS.md.

## Features

- [ ] [FEATURE-0031 - Dashboard Information Architecture and Run UX](./dashboard_information_architecture_0031.md)
- [ ] [FEATURE-0032 - Configuration and Risk Controls UX](./configuration_risk_controls_ux_0032.md)
- [ ] [FEATURE-0033 - Learning, Backtest, and Strategy Comparison UX](./learning_backtest_comparison_ux_0033.md)
- [ ] [FEATURE-0034 - Style Guide and Component Library](./style_guide_component_library_0034.md)
- [x] [FEATURE-0045 - Neko Quant brand identity (additive)](./neko_quant_identity_0045.md)
- [ ] [FEATURE-0046 - Neko animated mascot (designer + motion)](./neko_animated_mascot_0046.md)
- [ ] [FEATURE-0047 - Neko sound design (SFX)](./neko_sound_design_0047.md)
- [ ] [FEATURE-0048 - Neko hacker mode terminal (xterm.js)](./neko_hacker_mode_0048.md)
- [ ] [FEATURE-0049 - Neko achievement badges (persistence)](./neko_achievements_0049.md)

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
