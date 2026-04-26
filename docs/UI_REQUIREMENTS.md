# UI_REQUIREMENTS

The dashboard ([`frontend/`](../frontend)) is the human view over the
read-only [`backend`](../backend) API. It must be fast, dense, dark by
default, and component-first.

For the full build-ready styleguide spec, use
[`FEATURE-0034`](../specs/trading-lab-platform/tasks/frontend-operator-experience/style_guide_component_library_0034.md).
This document is the short operator/developer reference.

## Pages (one route each)

| Route             | Purpose                                                              |
|-------------------|----------------------------------------------------------------------|
| `/`               | **System overview** — KPIs (live/paper strategies, active signals, latest backtest Sharpe / DD / CAGR) |
| `/trades`         | **Trades history** — TanStack Table over `/api/trades`, filterable by strategy / symbol / venue |
| `/strategies`     | **Strategy performance** — card grid + per-strategy detail with latest backtest metrics |
| `/signals`        | **Signal explorer** — table over `/api/signals` showing lifecycle status |
| `/diagnostics`    | **Model diagnostics** — engine metrics + recent backtest IC / metrics |
| `/backtests`      | **Backtest lab** — list of runs (`/api/backtests`) + per-run detail at `/backtests/[runId]` |
| `/health`         | **System health** — API / DuckDB / Redis status, exposure, risk rejects |

## Mandatory data sources

The frontend reads only from the FastAPI backend. It does **not** open
DuckDB directly, and it does **not** call any exchange. All requests go
through [`frontend/lib/api.ts`](../frontend/lib/api.ts).

## Visual rules

- **Theme:** cyberpunk hacker ops. Dark terminal base, neon telemetry, dense
  panels, high contrast, and practical data visibility over decoration.
- **Color tokens:** mint/green for primary and safe-positive states; foxfire
  amber for warning/paper; magenta for AI/analysis; red for danger/rejected;
  lavender/cyan for secondary telemetry. Product code consumes tokens, not
  ad hoc hex values.
- **Typography:** UI sans for chrome; **monospace** for every number, ID,
  symbol, timestamp, hash, and command. Numbers are right-aligned in tables.
- **Spacing/density:** dashboards use compact cards, tight table rows, and
  visible section boundaries. Avoid marketing-page whitespace.
- **Elevation/borders:** panels use subtle black-glass backgrounds, fine
  borders, and neon glows only for selected/live/critical states.
- **Motion:** motion is functional only: live pulse, loading scanline,
  command-palette transitions. No data-obscuring decorative animation.
- **Status colors:** `success` (green), `warning` (amber), `danger` (red),
  `primary` (brand). Live status uses `primary`; paper uses `warning`;
  retired uses `danger`.
- **Charts:** TradingView Lightweight Charts only (no Chart.js, no D3).
  Equity curves are area charts; price/OHLC are candle series.
- **Tables:** TanStack Table with sortable columns; sortable defaults are
  recorded in code so reloads are stable.

## Mandatory components

- `/styleguide` is the executable source of truth for shared components.
  Components are added there before product pages use them.
- `Header` shows API health badge + version + env.
- `Sidebar` is the primary navigation; pages do not link to each other except
  via deep links (`strategies → /strategies/[id]`, `backtests → /backtests/[runId]`).
- Tables include an empty-state row, never a blank table.
- Numeric cells render through `formatNumber` / `formatPct` / `formatDate`
  in [`frontend/lib/utils.ts`](../frontend/lib/utils.ts).
- `MetricTile`, `RunStatusPill`, `RiskLimitMeter`, `StrategyCard`,
  `AlertBanner`, `LogStream`, `CommandPalette`, and `AiInsightPanel` must be
  demoable with local mock fixtures before product usage.
- Chart components wrap TradingView Lightweight Charts and publish project
  defaults in the styleguide.

## Required styleguide entries

Each styleguide entry includes:

- Component name, status (`draft | reviewed | production`), source path, and
  import path.
- Generated prop table from TypeScript types.
- Local mock fixture path under `frontend/styleguide/mocks/`.
- Demo states: default plus loading, empty, error, stale, and populated where
  applicable.
- Accessibility notes: ARIA roles, keyboard behavior, focus states.
- Test affordance or documented component-test command.

Product pages may import only `production` shared components unless the
feature ticket explicitly marks the page partial.

## Key surface patterns

- **Dashboard:** health header, KPI rail, live run timeline, risk panel,
  alerts/log split, strategy evidence cards.
- **Runs/backtests:** dense list table, detail metric cards, config JSON,
  state transitions, artifact links, comparison view with missing-data states.
- **Risk:** current exposure, limit, margin to limit, latest reject rule, and
  kill-switch status. No direct order controls.
- **Logs/alerts:** severity, source subsystem, run id, event id/audit hash, and
  recommended operator action.
- **Command/search:** navigate, filter, and request read-only diagnostics.
  Mutating commands route to approval flows and never directly place orders.

## What the dashboard never does

- No order placement. The UI is read-only.
- No raw API keys in client code. Anything sensitive lives in the backend.
- No live trade execution buttons. Trade controls live in the trading
  engine and are gated by `RiskEngine`.
- No LLM responses surfaced as actionable trading signals (see
  [`.cursor/rules/llm-usage.mdc`](../.cursor/rules/llm-usage.mdc)).
