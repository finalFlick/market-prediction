# trading-lab — System Design

## 1. Goals

- **Discover** trading signals via reproducible research.
- **Validate** them with realistic backtests (fees, slippage, latency).
- **Deploy** validated strategies as automated bots with strict, deterministic
  risk management.
- **Observe** live performance and detect drift before it costs money.

Non-goals (for now): HFT / sub-second latency, options market-making,
proprietary low-latency networking.

## 2. Pipeline

```
┌────────────┐   ┌────────────────────┐   ┌──────────────┐
│ market_data│ → │ feature_engineering│ → │ signal_models│
└────────────┘   └────────────────────┘   └──────┬───────┘
                                                 │
                                                 ▼
                                       ┌──────────────────┐
                                       │  strategy_engine │
                                       └────────┬─────────┘
                                                ▼
                                       ┌──────────────────┐
                                       │   risk_engine    │
                                       └────────┬─────────┘
                                                ▼
                                       ┌──────────────────┐
                                       │    execution     │
                                       └────────┬─────────┘
                                                ▼
                                       ┌──────────────────┐
                                       │   monitoring     │ ← cross-cutting
                                       └──────────────────┘
```

Each box is one Python package with a stable input/output contract.

## 3. Module contracts

### 3.1 `data/` — ingestion and storage

- **Inputs**: REST + websocket feeds from Binance and Coinbase.
- **Outputs**:
  - `OHLCVBar` records persisted in DuckDB (`bars` table) and as parquet.
  - Live tick stream available via `data.stream.subscribe(symbol)`.
- **Schema** (DuckDB, defined in `data/schema.sql`):

  - `market_data(exchange, symbol, timeframe, ts, open, high, low, close, volume, quote_volume)`
    — primary key `(exchange, symbol, timeframe, ts)`, upsert idempotent.
  - `signals(signal_id, name, status, timeframe, intuition, owner, updated_at)`
    — backlog mirror for the `SIGNALS.md` document.
  - `strategies(strategy_id, name, universe, timeframe, status, config_path, created_at, updated_at)`
    — registered strategies and their lifecycle status.
  - `trades(trade_id, client_order_id, strategy_id, exchange, symbol, side,
    quantity, price, fee, pnl, venue, ts)` — every fill, tagged
    `venue ∈ {backtest, paper, live}`.
  - `backtests(run_id, strategy_id, git_commit, config_hash, started_at,
    finished_at, sharpe, sortino, max_drawdown, cagr, final_equity, n_trades,
    artifact_dir)` — one row per `python -m backtests.run` invocation.

  All five tables are accessed via repository classes in
  `data/repositories/` so business code never writes raw SQL.

### 3.2 `research/` — features and models

- **Features**: pure functions `(df: pd.DataFrame) -> pd.Series | pd.DataFrame`
  with shift-check validation.
- **Labels**: forward-return based, computed on bars after the feature
  timestamp.
- **Models**: a unified `Model` protocol with `fit`, `predict`, `save`, `load`.
  Implemented for `lightgbm`, `xgboost`, and `pytorch` backbones.
- **Registry**: each trained artifact lives in
  `research/models/registry/<model_id>/` with a `manifest.json` containing
  config hash, data range, features, metrics, git commit, seeds.

### 3.3 `strategies/` — composition

- A `Strategy` is the smallest unit of "we want exposure shaped this way".
- API: `Strategy.target_positions(state: MarketState) -> dict[str, float]`
  returning target weights per symbol.
- Baseline `momentum_xover` ships as the reference implementation.

### 3.4 `risk/` — checks and sizing

- `RiskEngine.check_and_size(targets, portfolio, market) -> list[Order]`
  is the single entrypoint.
- Mandatory checks: gross exposure, per-symbol cap, leverage, daily loss,
  drawdown stop, kill-switch.
- Sizing: volatility-targeted with a minimum-notional floor.

### 3.5 `backtests/` — simulation

- Wraps `vectorbt` portfolio simulation.
- Loads OHLCV from DuckDB, plugs in the strategy and risk engine, applies
  costs from `configs/costs.yaml`, writes the standard artifact set.
- Determinism: every run records seeds, config hash, data snapshot id.

### 3.6 `execution/` — brokers

- `Broker` protocol with: `place_order`, `cancel_order`, `get_positions`,
  `get_balances`, `stream_events`.
- Implementations:
  - `paper` — simulates fills against the live tick stream using project costs.
  - `binance` — REST + websocket, idempotent client order ids.
  - `coinbase` — Advanced Trade REST + websocket.
- The `runner` ties strategy → risk → broker on a fixed cadence
  (e.g. minute-aligned).

### 3.7 `monitoring/` — observability

- Structured logging (`structlog`) emits JSON to stdout and a rotating file.
- Metric gauges: equity, exposure, gross/net, drawdown, fill rate, slippage.
- Drift detector compares realized vs backtest distribution and triggers an
  alert + (optional) kill-switch.

## 4. Data flow at runtime

```
broker websocket ──► data.stream ──► strategy.target_positions
                                            │
                                            ▼
                                      risk.engine.check_and_size
                                            │
                                            ▼
                                      execution.broker.place_order
                                            │
                                            ▼
                                      monitoring.metrics + logger
```

## 5. Configuration

YAML configs in `configs/`, loaded via `pydantic` models in
`<module>/config.py`. Examples:

- `configs/costs.yaml` — fees, slippage, latency, funding.
- `configs/risk.yaml` — limits per environment.
- `configs/strategies/<name>.yaml` — symbol universe, parameters.
- `configs/backtest.yaml` — date range, capital, output dir.

## 6. Reproducibility

- Each backtest run id is `<utc-timestamp>-<git-sha>-<config-hash>`.
- Manifest records: config hash, git commit, data snapshot id, all seeds,
  package versions of `pandas`, `numpy`, `vectorbt`, model libs.
- Re-running with the same manifest must produce byte-identical
  `metrics.json`. CI enforces this on a tiny fixture.

## 7. Promotion path

```
hypothesis → research → backtest → paper → live → (retired)
```

Each transition writes a row to `DECISIONS.md` and updates `SIGNALS.md`. The
only path that allows live capital is gated by `RiskAgent` review.

## 8. Service topology and APIs

### 8.1 Backend API (`backend/`)

A FastAPI app exposes read-only views over the DuckDB tables:

| Endpoint              | Purpose                                                 |
|-----------------------|---------------------------------------------------------|
| `GET /api/trades`     | Recent fills, filterable by strategy / symbol / venue   |
| `GET /api/strategies` | Registered strategies and lifecycle status              |
| `GET /api/signals`    | Hypothesis backlog mirroring `SIGNALS.md`               |
| `GET /api/backtests`  | Backtest runs and headline metrics                      |
| `GET /api/system/*`   | Health and runtime metrics snapshot                     |

The trading engine is the **only** writer to the underlying tables. Adding a
mutation route to the API requires `RiskAgent` review.

### 8.2 Frontend dashboard (`frontend/`)

Next.js 14 (App Router) + TypeScript + Tailwind + shadcn-style primitives.
Charts use TradingView Lightweight Charts; tables use TanStack Table.

Pages:

| Route             | Page                                                            |
|-------------------|-----------------------------------------------------------------|
| `/`               | System overview (health, KPIs, latest backtest)                 |
| `/trades`         | Trades history with filters                                     |
| `/strategies`     | Strategy performance grid + per-strategy detail                 |
| `/signals`        | Signal explorer                                                 |
| `/diagnostics`    | Model diagnostics (live metrics + recent backtests)             |
| `/backtests`      | Backtest lab; per-run detail at `/backtests/[runId]`            |
| `/health`         | System health detail (DuckDB, Redis, exposure, risk rejects)    |

The dashboard talks only to `backend` (`NEXT_PUBLIC_API_URL`); it does not
read DuckDB directly.

### 8.3 Container topology

```
                 ┌────────────────┐
        ─────►   │   frontend     │   :3000  (Next.js, standalone)
        │        └───────▲────────┘
        │                │ HTTP
        │        ┌───────┴────────┐
        │        │    backend     │   :8000  (FastAPI)
 user ──┘        └─┬───────┬──────┘
                   │       │
                   │       │
              ┌────▼─┐  ┌──▼────────────┐    ┌────────────┐
              │redis │  │trading-engine │ ←  │  ollama    │  external
              └──┬───┘  └──┬────────────┘    │  hermes    │
                 │         │                 └────────────┘
                 │   ┌─────▼─────┐
                 └──►│  duckdb   │  shared volume
                     └───────────┘
```

All containers join the `trading-net` docker network. `ollama` and `hermes`
are pre-existing and joined `external: true`.

## 9. AI evaluation (`ai_evals/`)

Two layers:

- **deepeval** — pytest-style structural assertions (JSON shape, forbidden
  phrases). Runs in CI on every PR. Offline mode reads
  `ai_evals/fixtures/offline_responses.json`; online mode hits Ollama.
- **promptfoo** — declarative YAML evals exercising every prompt with a
  fixture provider in CI and (optionally) the live Ollama provider locally.
  Reports are uploaded as CI artifacts.

Both layers reference the prompt registry in `research/llm/prompts.py`; that
is the single source of truth for prompt content and version.

## 10. Future extensions

- Order book + trade-tape ingestion.
- Multi-asset and multi-exchange portfolio optimization.
- Online learning for drift-aware models.
- Event-driven backtester for strategies that vectorbt cannot represent
  (e.g. complex order types, market-making queue position).
- Live equity-curve and trade-tape streaming to the frontend over websockets
  (currently the dashboard polls REST endpoints).
