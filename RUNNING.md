# RUNNING

How to build, run, test, and validate the system. Tested on the Unraid host
that owns the `trading-net` docker network.

## First-time setup

```bash
git clone <repo> trading-lab && cd trading-lab
cp .env.example .env                       # then fill in keys

docker network create trading-net          # one-time, shared with ollama/hermes
```

Python toolchain (only needed for ad-hoc CLI runs outside docker):

```bash
python -m venv .venv
.venv\Scripts\activate                     # Windows
# source .venv/bin/activate                # macOS / Linux
pip install -e ".[dev,ai-eval]"
```

## Run the full stack

```bash
docker compose build
docker compose up -d
docker compose logs -f trading-engine
```

| Service        | URL                                                   |
|----------------|-------------------------------------------------------|
| frontend       | http://localhost:3000                                 |
| backend (API)  | http://localhost:8000/api/system/health               |
| redis          | localhost:6379                                        |
| ollama (ext.)  | http://ollama:11434 (inside `trading-net`)            |

## Tests

```bash
pytest -q                                  # unit + strategy + security
pytest -q -m e2e                           # API + backtest end-to-end
pytest -q ai_evals/deepeval                # offline LLM contract tests
```

## Lint & typecheck

```bash
ruff check .
ruff format --check .
mypy --strict --explicit-package-bases data research strategies risk \
                                       backtests execution monitoring backend
```

## AI evaluations

```bash
# offline (CI default) — uses recorded fixtures
pytest -q ai_evals/deepeval

cd ai_evals/promptfoo && promptfoo eval --no-cache
# online — hits the local Ollama instance
OFFLINE_LLM=false promptfoo eval
```

## Backtests

```bash
# Smoke test (deterministic, ~1 second)
python -m backtests.smoke

# Full run
python -m backtests.run \
    --strategy strategies.examples.momentum_xover \
    --config configs/backtest.yaml
```

## Data ingestion

Public REST (no exchange API keys; default):

```bash
python -m data.ingest.run --source binance --symbol BTCUSDT --timeframe 1h --days 7
python -m data.ingest.run --source coinbase --symbol BTC-USD --timeframe 1h --days 7
python -m data.ingest.run --source yahoo --symbol AAPL --timeframe 1d --days 30   # needs: pip install 'trading-lab[public-data]'
```

If `api.binance.com` is geo-blocked, set `BINANCE_PUBLIC_REST_BASE` (e.g. `https://api.binance.us`).

```bash
python -m research.features.build --output data/processed/features.parquet
python -m research.models.train --config configs/lgbm_baseline.yaml
```

## Paper trading

```bash
python -m execution.runner --broker paper \
    --strategy strategies.examples.momentum_xover
```

## Frontend (standalone dev)

```bash
cd frontend
npm install
npm run dev                                # http://localhost:3000
npm run lint && npm run typecheck && npm run build
```
