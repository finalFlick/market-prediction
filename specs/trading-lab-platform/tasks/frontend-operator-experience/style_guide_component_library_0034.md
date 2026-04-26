# FEATURE-0034: Style Guide and Component Library

## Parent Epic

frontend-operator-experience

## Status

Ready for implementation - spec strengthened 2026-04-26

## Summary

Define the build-ready design system, component demos, visual tokens, interaction states, and UX patterns that every frontend page must use before product-page implementation.

## Why

The dashboard is the operator's control room. A weak styleguide forces every frontend agent to improvise layout, color, density, risk language, and loading/error states. A strong component-first guide makes the cyberpunk hacker theme repeatable, keeps the UI beginner-safe, and creates testable examples that do not depend on the backend.

## What

Ship a self-contained `/styleguide` route that demonstrates the reusable UI system with local mock data. The route is both design documentation and an executable component harness: tokens, primitives, data displays, charts, command surfaces, risk panels, alert states, logs, and page-level layout patterns all render in isolation.

## User / System Story

As a platform operator and future implementation agent,
I want a demoable component library with concrete visual and UX guidance,
so that frontend pages can be built consistently without guessing and reviewed against live examples.

## Source Traceability

- requirements.md: Req 34, Req 46, Req 50
- design.md: Component 21; Frontend Page Inventory; Component Library and Component Status; Performance Considerations
- Repo conventions: `.cursor/rules/frontend.mdc`, `.cursor/rules/component-first.mdc`, `.cursor/rules/workflow.mdc`, `.cursor/rules/security.mdc`, `.cursor/rules/spec-sessions.mdc`, and AGENTS.md.

## Requirements Covered

- Req 34 - Beginner-safe UX
- Req 46 - quality tests for key frontend components
- Req 50 - component-first styleguide and component library

## Design Direction: Cyberpunk Hacker Ops

The UI should feel like a disciplined market-ops terminal rather than a generic SaaS dashboard.

- **Mood:** dark, dense, high-contrast, terminal-like, but readable for a beginner.
- **Visual metaphor:** neon telemetry over a black-glass trading console.
- **Primary colors:** mint/green for safe/positive/primary, magenta for AI/analysis, foxfire amber for warning/paper, red for danger/rejected, lavender/cyan for secondary telemetry.
- **Density:** compact cards and tables; never sparse marketing layouts.
- **Motion:** small and functional: pulses for live streams, scanline shimmer for loading, no decorative motion that hides data.
- **Trust:** risk limits, mode (`backtest | paper | live`), source freshness, and data provenance must be visible near actions and summaries.

## Design Tokens

Tokens live in `frontend/styles/tokens.css` or the Tailwind theme. Components consume tokens only; no ad hoc hex colors in product pages.

| Token group | Required tokens | Usage |
|---|---|---|
| Color | `night`, `panel`, `panel-2`, `mint`, `foxfire`, `magenta`, `lavender`, `cyan`, `danger`, `border`, `muted` | backgrounds, borders, status, chart accents |
| Typography | `font-sans`, `font-mono`, `text-xs/sm/base/lg`, `tracking-terminal` | chrome uses sans; IDs, symbols, metrics use mono |
| Spacing | `space-1/2/3/4/6/8`, `grid-gap-card`, `page-pad` | consistent card grids and responsive page gutters |
| Elevation | `shadow-neon`, `shadow-panel`, `glow-danger`, `glow-warning` | active cards, critical alerts, selected rows |
| Borders | `radius-sm/md/lg`, `border-subtle`, `border-live`, `border-risk` | cards, tables, form controls, risk panels |
| Motion | `duration-fast`, `duration-normal`, `ease-terminal`, `pulse-live`, `scan-loading` | streaming badges, skeletons, command palette |
| State | `state-loading`, `state-empty`, `state-error`, `state-degraded`, `state-stale` | demo state fixtures and badges |

## Component Categories and Required Demos

Every component entry includes: name, status badge, source path, import path, generated prop table, mock fixture path, accessibility notes, keyboard behavior, and demo states.

### Primitives

- `Badge`: variants `default | success | warning | danger | live | paper | retired | degraded`.
- `Card`: variants `panel | metric | risk | alert | glass`.
- `Button`: variants `primary | ghost | danger | command`; states default/hover/focus/disabled/loading.
- `Input` / `Select` / `Textarea`: terminal focus ring, validation, helper text.
- `Skeleton` / `EmptyState` / `ErrorState`: all pages must use these instead of blank areas.

### Data Components

- `MetricTile`: label, value, delta, unit, stale badge, source timestamp.
- `RunStatusPill`: `queued | running | succeeded | failed | paused | recovered`.
- `RiskLimitMeter`: current exposure vs limit, danger threshold, rejection reason.
- `TradesTable`: sortable TanStack table with empty/loading/error/populated demos.
- `EvidenceTable`: OOS metrics, artifact link, config hash, audit hash.

### Charts

- `EquityCurveChart`: area chart with drawdown overlay and benchmark line.
- `RiskExposureChart`: stacked exposure by symbol or strategy.
- `PnLDistributionChart`: histogram-like panel using approved chart library only.
- `FreshnessSparkline`: source latency/freshness over time.

Charts use TradingView Lightweight Charts wrappers only. The styleguide documents wrapper defaults and mock datasets.

### Operator Surfaces

- `StrategyCard`: status, capital mode, latest backtest metrics, promotion gate badge.
- `RiskPanel`: limits, active rejects, kill-switch state, no order buttons.
- `RunTimeline`: state transitions, timestamps, recovery annotations.
- `AlertBanner`: INFO/WARNING/CRITICAL with remediation copy and audit link.
- `LogStream`: monospaced structured events, filters, copy event id.
- `CommandPalette`: search/command UI for navigation and read-only diagnostics; mutating commands route to approval, never direct execution.
- `AiInsightPanel`: LLM summary with source citations and explicit "not a trade signal" affordance.

## Page-Level Layout Patterns

### Dashboard Overview

```
Header(API health, env, version)
Sidebar(route groups)
Main grid:
  - KPI rail: active runs, latest Sharpe, max DD, risk rejects
  - Live run timeline
  - Risk panel
  - Alerts + logs split panel
  - Strategy evidence cards
```

### Runs and Backtests

- List pages use dense tables with stable default sorting.
- Detail pages use summary metric cards, artifact links, config JSON, state transitions, and run logs.
- Compare pages use side-by-side metrics with visual deltas and explicit missing-data states.

### Strategy and Risk

- Strategy cards always show evidence level (`hypothesis | research | backtest | paper | live | retired`), last OOS metrics, and current risk cap.
- Risk panels always show current value, limit, margin to limit, and most recent reject rule.
- Live controls are out of scope unless a later gated live workflow is approved.

### Logs, Alerts, Command/Search

- Logs are filterable by severity, run id, component, and audit hash.
- Alerts include severity, affected subsystem, recommended operator action, and source event id.
- Command/search UI can navigate, filter, and create read-only diagnostics. Mutating actions require backend approval queues per the approved design.

## Demo Data and File Layout

Required structure when implemented:

```text
frontend/styleguide/
  registry.ts
  mocks/
    metric-tile.ts
    run-status-pill.ts
    risk-panel.ts
    equity-curve-chart.ts
    trades-table.ts
    log-stream.ts
  demos/
    MetricTileDemo.tsx
    RiskPanelDemo.tsx
    CommandPaletteDemo.tsx
```

Mock data must be deterministic and local. `/styleguide` must boot with `BACKEND_URL=` unset and no running backend.

## Component Status Model

| Status | Meaning | Product-page use |
|---|---|---|
| `draft` | visual/UX sketch, API may change | styleguide only |
| `reviewed` | accessible, typed, tested, but awaiting product evidence | limited internal demos |
| `production` | docs, tests, states, responsive, and product usage verified | allowed in operator pages |

Product pages may import only `production` components unless a feature ticket explicitly marks the page partial.

## Acceptance Criteria

- Given the source documents and repo standards, when an implementation plan is prepared, then it traces this feature to Req 34, Req 46, Req 50, Component 21, and the Frontend Page Inventory.
- Given `/styleguide` is implemented, when `npm run dev` starts with no backend running, then the route renders every registered component from local mock data.
- Given a component is registered, when the styleguide renders it, then the page displays component name, status, source path, import path, generated prop table, mock fixture path, demo states, accessibility notes, and keyboard interactions.
- Given a new file is added under `frontend/components/**/*.tsx`, when validation runs, then a matching styleguide registry entry and mock fixture are present or the check fails.
- Given a product page imports a shared component, when validation runs, then that component exists in the styleguide with `production` status or the page is marked partial in its feature ticket.
- Given a chart component is added, when review runs, then it wraps TradingView Lightweight Charts and documents project-specific defaults in the styleguide.
- Given a component has loading, empty, error, stale, or populated states, when the styleguide renders, then each applicable state is demoed from fixtures.
- Given a component displays market, run, risk, or audit data, when reviewed, then numeric values are monospaced, dates are formatted centrally, and status colors use design tokens.
- Given a component could imply trading action, when reviewed, then it includes copy that preserves the read-only frontend and non-bypassable risk model.

## Validation Expectations

- Frontend: `npm run lint`, `npm run typecheck`, `npm run build`.
- Component tests: Vitest + React Testing Library or an approved equivalent using the same mock fixtures as `/styleguide`.
- Accessibility: keyboard navigation and ARIA checks for command palette, tables, forms, alerts, dialogs, and charts.
- Cursor harness: `.cursor/rules/component-first.mdc` present and routed by `.cursor/context-router.json`.
- Backend independence: `/styleguide` manually verified with backend down and mock data only.
- General repo checks: `pytest -q`, `ruff check .`, and `mypy --strict .` unless a task-specific waiver is recorded.

## Dependencies

- `frontend/` Next.js app and Tailwind config.
- Existing UI primitives and chart wrappers.
- Future component test runner setup.
- `.cursor/rules/component-first.mdc` and frontend rule routing.

## Risks / Edge Cases

- A styleguide can become decorative if product pages bypass it; CI or Cursor checks must enforce component-first order.
- Cyberpunk visuals can reduce readability; contrast and table density must be tested with realistic data.
- Mock fixtures can drift from API contracts; contract tests or typed fixtures must keep them current.
- Inline network calls in components would make demos flaky and violate the read-only frontend contract.

## Observability / Diagnostics

The styleguide should expose a registry summary: component counts by status, missing demo states, stale fixtures, and failed component tests. The operator product should expose component errors as UI error states, never blank panels.

## Documentation Expectations

- Update `docs/UI_REQUIREMENTS.md` when tokens, component categories, or layout patterns change.
- Update `README.md` / `RUNNING.md` if styleguide commands or dev workflow changes.
- Update `SESSION_LOG.md` with verification evidence when implementation lands.
- Update `DECISIONS.md` only if this changes architecture, release gates, or approved frontend tooling.

## Done Means

- [ ] `/styleguide` route exists and is self-contained.
- [ ] Component registry and deterministic mock fixtures exist.
- [ ] Required token groups are implemented and documented.
- [ ] Existing shared components are backfilled with demos.
- [ ] At least one dashboard, run table, risk panel, chart, alert, log, and command/search surface is demoable.
- [ ] Component tests or documented manual checks cover key states.
- [ ] `.cursor/rules/component-first.mdc` guides agents and is referenced by frontend rules/docs.
- [ ] Source traceability remains accurate after implementation.
