# trading-lab

An AI-assisted quantitative trading research platform for discovering signals,
backtesting strategies, and deploying automated trading bots with strict risk
management.

> **New here?** Read [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) first — it's
> the operating manual that points to every other doc:
> [`WORKFLOW.md`](WORKFLOW.md), [`RUNNING.md`](RUNNING.md),
> [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md),
> [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md),
> [`docs/CODING_STANDARDS.md`](docs/CODING_STANDARDS.md),
> [`docs/RISK_POLICY.md`](docs/RISK_POLICY.md),
> [`docs/EVALUATION.md`](docs/EVALUATION.md),
> [`docs/INFRASTRUCTURE.md`](docs/INFRASTRUCTURE.md),
> [`docs/UI_REQUIREMENTS.md`](docs/UI_REQUIREMENTS.md),
> [`AGENTS.md`](AGENTS.md).

Contributions are welcome. This repo is **public** — see
[`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) for fork PR and CI security
expectations.

## Pipeline

```
market_data → feature_engineering → signal_models → strategy_engine
            → risk_engine → execution → monitoring
```

Each stage is an independent module that produces typed artifacts consumed by
the next stage. See `docs/DESIGN.md` for the full architecture.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate                  # Windows
# source .venv/bin/activate              # macOS / Linux

pip install -e ".[dev]"

# 1. Ingest data
python -m data.ingest.run --exchange binance --symbol BTCUSDT --timeframe 1h --days 365

# 2. Build features
python -m research.features.build --input data/raw --output data/processed/features.parquet

# 3. Train a signal model
python -m research.models.train --config configs/lgbm_baseline.yaml

# 4. Backtest
python -m backtests.run --strategy strategies.examples.momentum_xover --config configs/backtest.yaml

# 5. Paper trade
python -m execution.runner --broker paper --strategy strategies.examples.momentum_xover
```

## Run the full stack

```bash
docker network create trading-net 2>/dev/null || true     # one-time
python dev.py base                                       # shared Python base image
docker compose build
docker compose up -d
docker compose logs -f trading-engine
```

| Service        | URL / port                       |
|----------------|----------------------------------|
| frontend       | http://localhost:3000            |
| backend (API)  | http://localhost:8000/api/system/health |
| redis          | localhost:6379                   |
| ollama         | external (`http://ollama:11434`) |

`docker-compose.yml` joins the existing `trading-net` so `ollama` and
`hermes` can be managed independently.

## Fast Docker Development

For day-to-day work on Windows, macOS, or Linux, use the dev override instead
of rebuilding images after every edit:

```bash
python dev.py up
```

The dev stack bind-mounts source code, keeps Python dependencies in the
Docker-native `trading-py-venv` volume, keeps pip wheels in
`trading-pip-cache`, and runs backend/frontend hot reload. On Windows Docker
Desktop it also masks host-only directories like `.venv`, `.git`, cache
folders, and `frontend/node_modules` so pytest does not crawl gigabytes of
Windows filesystem entries through the WSL2 mount bridge.

Useful commands:

```bash
python dev.py base                          # rebuild trading-base after dependency changes
python dev.py logs backend
python dev.py exec backend -- pytest -q -m "not slow and not integration"
python dev.py jupyter                       # http://localhost:8888
python dev.py reset-deps                    # refresh Docker dependency volumes
```

See [`RUNNING.md`](RUNNING.md) for the full workflow and validation commands.

## Repository layout

| Path             | Purpose                                                 |
|------------------|---------------------------------------------------------|
| `data/`          | Exchange ingestion, DuckDB schema, repositories         |
| `research/`      | Feature engineering, signal model training, LLM helpers |
| `strategies/`    | Composition of signals into trade rules                 |
| `risk/`          | Position sizing, stops, drawdown / leverage limits      |
| `backtests/`     | Vectorbt-based simulation harness, smoke entrypoint     |
| `execution/`     | Broker adapters (paper, Binance, Coinbase) + runner     |
| `monitoring/`    | Structured logging, metrics, drift detection            |
| `backend/`       | FastAPI read-only API (`/api/...`)                      |
| `frontend/`      | Next.js + TS dashboard                                  |
| `ai_evals/`      | promptfoo + deepeval prompt evaluation harness          |
| `configs/`       | YAML configs for runs, models, strategies, risk         |
| `docs/`          | Design, strategy, MCP integration docs                  |
| `tests/`         | unit / strategy / e2e / security pytest suites          |
| `.cursor/rules/` | Persistent guidance for the AI agents                   |
| `.github/workflows/` | CI: lint, mypy, pytest, ai-evals, docker builds     |

## Frontend Styleguide

Frontend work is component-first. Shared UI belongs in the executable
`/styleguide` route before product pages use it. The source of truth for the
current cyberpunk hacker ops design system is
[`FEATURE-0034`](specs/trading-lab-platform/tasks/frontend-operator-experience/style_guide_component_library_0034.md),
with the shorter operator-facing summary in
[`docs/UI_REQUIREMENTS.md`](docs/UI_REQUIREMENTS.md). The frontend must remain
read-only: no order placement, no secrets, no exchange calls, and no LLM text
presented as actionable trading advice.

## Stack

- **Backend**: Python 3.11+, FastAPI, DuckDB, Redis
- **Data**: `pandas`, `pyarrow`, `duckdb`
- **Backtesting**: `vectorbt`
- **Models**: `lightgbm`, `xgboost`, `pytorch`
- **Exchanges**: `python-binance`, `coinbase-advanced-py`, `ccxt`
- **LLM (research only)**: local Ollama via `research/llm/`
- **Frontend**: Next.js 14, React 18, TypeScript, Tailwind, shadcn-style UI,
  TradingView Lightweight Charts, TanStack Table
- **CI**: GitHub Actions, ruff, mypy, pytest, promptfoo, gitleaks
- **Configs**: `pydantic`, `pyyaml`

## Development workflow

Every change follows the loop in `.cursor/rules/workflow.mdc`:

```
analyze → identify files → minimal change → tests → lint/typecheck → e2e
```

A task is **not complete** until `pytest`, `ruff`, and `mypy` all pass and
at least one `tests/e2e/` or `backtests/smoke.py` invocation exercises the
new code path.

## Operating principles

1. **Deterministic risk**: every order passes through `risk/` checks. No bypass paths.
2. **Realistic backtests**: fees, slippage, and latency are mandatory inputs.
3. **No look-ahead**: feature timestamps are strictly point-in-time.
4. **Reproducibility**: every backtest writes a manifest with config hash, data
   snapshot, code commit, and seeds.
5. **Paper before live**: a strategy must produce N consecutive paper-trading
   days within tolerance of its backtest before any live capital is allocated.
6. **LLMs are research-only**: per `.cursor/rules/llm-usage.mdc`, no module under
   `execution/` may import `research.llm`. CI enforces this.

See `AGENTS.md` for the agent-driven workflow and `TODO.md` for the current sprint.
