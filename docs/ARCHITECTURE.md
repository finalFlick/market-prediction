# ARCHITECTURE

High-signal overview of the tech stack and how the pieces connect. Full
contracts and module-by-module detail live in [`DESIGN.md`](DESIGN.md).

## Stack

| Layer            | Tools                                                          |
|------------------|----------------------------------------------------------------|
| Backend          | Python 3.11+, **FastAPI**                                      |
| Data             | **DuckDB** + Parquet (snapshots)                               |
| Trading framework| **vectorbt** (portfolio simulation)                            |
| Signal ML        | **LightGBM**, **XGBoost**                                      |
| Deep ML          | **PyTorch**                                                    |
| LLM (research)   | **Ollama** (local, GPU)                                        |
| Execution        | **CCXT**; venue-specific clients (`python-binance`, `coinbase-advanced-py`) for features ccxt does not cover |
| Frontend         | **Next.js 14**, React 18, TypeScript, Tailwind, shadcn-style UI, **TradingView Lightweight Charts**, TanStack Table |
| Infra            | **Docker** + Docker Compose, **Unraid** host                   |
| CI               | GitHub Actions, ruff, mypy, pytest, promptfoo, gitleaks        |

## Pipeline (one-way)

```
market_data → feature_engineering → signal_models → strategy_engine
            → risk_engine → execution → monitoring
```

Each arrow is a typed contract. Risk is the only path to execution.

## Container topology

```
                 ┌────────────────┐
        ─────►   │   frontend     │   :3000  (Next.js standalone)
        │        └───────▲────────┘
        │                │ HTTP (NEXT_PUBLIC_API_URL)
        │        ┌───────┴────────┐
        │        │    backend     │   :8000  (FastAPI, read-only)
 user ──┘        └─┬───────┬──────┘
                   │       │
              ┌────▼─┐  ┌──▼─────────────┐    ┌──────────────┐
              │redis │  │trading-engine  │ ←  │  ollama      │  external
              └──┬───┘  └──┬─────────────┘    │  hermes      │
                 │         │                  └──────────────┘
                 │   ┌─────▼─────┐
                 └──►│  duckdb   │  shared volume
                     └───────────┘
```

All containers join the `trading-net` docker network. `ollama` and `hermes`
are pre-existing on the Unraid host and joined `external: true`.

## Data flow at runtime

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
                                            │
                                            ▼
                                      DuckDB (trades) + Redis (events)
                                            │
                                            ▼
                                      backend (FastAPI) → frontend
```

## What this enforces

- **Modularity.** Each module is a Python package with no upstream imports
  from later stages.
- **Determinism.** Every backtest writes a manifest with config hash, git
  commit, and seeds; re-runs produce byte-identical metrics.
- **Isolation of LLMs.** `execution/` cannot import `research.llm`
  (see [`.cursor/rules/llm-usage.mdc`](../.cursor/rules/llm-usage.mdc)).
- **Read-only API.** The trading engine is the only writer to DuckDB; the
  backend exposes views.

For module-level contracts, schemas, and the promotion path see
[`DESIGN.md`](DESIGN.md). For runtime topology and env vars see
[`INFRASTRUCTURE.md`](INFRASTRUCTURE.md).
