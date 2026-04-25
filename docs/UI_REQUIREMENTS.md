# UI_REQUIREMENTS

The dashboard ([`frontend/`](../frontend)) is the human view over the
read-only [`backend`](../backend) API. It must be fast, dense, and dark by
default.

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

- **Theme:** dark by default (`html.dark`). The brand color is the
  trading-green `hsl(160 84% 50%)` used for primary actions and equity gains.
- **Typography:** UI sans for chrome; **monospace** for any number, ID,
  symbol, or timestamp. Numbers are right-aligned in tables.
- **Status colors:** `success` (green), `warning` (amber), `danger` (red),
  `primary` (brand). Live status uses `primary`; paper uses `warning`;
  retired uses `danger`.
- **Charts:** TradingView Lightweight Charts only (no Chart.js, no D3).
  Equity curves are area charts; price/OHLC are candle series.
- **Tables:** TanStack Table with sortable columns; sortable defaults are
  recorded in code so reloads are stable.

## Mandatory components

- `Header` shows API health badge + version + env.
- `Sidebar` is the only navigation; pages do not link to each other except
  via deep links (`strategies → /strategies/[id]`, `backtests → /backtests/[runId]`).
- Tables include an empty-state row, never a blank table.
- Numeric cells render through `formatNumber` / `formatPct` / `formatDate`
  in [`frontend/lib/utils.ts`](../frontend/lib/utils.ts).

## What the dashboard never does

- No order placement. The UI is read-only.
- No raw API keys in client code. Anything sensitive lives in the backend.
- No live trade execution buttons. Trade controls live in the trading
  engine and are gated by `RiskEngine`.
- No LLM responses surfaced as actionable trading signals (see
  [`.cursor/rules/llm-usage.mdc`](../.cursor/rules/llm-usage.mdc)).
