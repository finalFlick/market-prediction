# RUNNING

How to build, run, test, and validate the system. Tested on the Unraid host
that owns the `trading-net` docker network.

## First-time setup

```bash
git clone <repo> trading-lab && cd trading-lab
cp .env.example .env                       # then fill in keys

docker network create trading-net          # one-time, shared with ollama/hermes
```

## Fast development loop

Use this workflow for iterative Python/TS edits without full rebuilds.

```bash
python dev.py base   # first time or after pyproject.toml / Dockerfile.base changes
python dev.py up
```

This starts:

- `backend` with `uvicorn --reload`
- `trading-engine` shared code execution loop
- `research` idle container for training/Jupyter use
- `frontend-init` (one-shot): runs `npm ci` into the `trading-node-modules` volume
  when `node_modules` is cold, then exits; skipped quickly when dependencies are
  already present
- `frontend` in HMR mode (`next dev`), after `frontend-init` completes successfully
- `redis`, `duckdb`, and required volumes

**First-start cost:** the first `python dev.py up` on a fresh machine (or after
`python dev.py reset-deps`) may spend a few minutes in `frontend-init` while
`npm ci` fills `trading-node-modules`. Later `up` runs reuse the volume and the
init step returns almost immediately. If you start only `frontend` without the
full stack, the inline `npm ci` guard in the frontend command still bootstraps
`node_modules` as a fallback.

Day-to-day workflow:

- Edit code in the repo; save file.
- Python services: backend auto-reloads from `backend`, `risk`, `runs`, `data`.
- Frontend components/pages update with Next.js HMR.
- Training and notebooks: `python dev.py jupyter`
- Run container checks quickly:

  ```bash
  python dev.py exec backend -- pytest -q -m "not slow and not integration"
  python dev.py logs backend
  ```

When adding a dependency to `pyproject.toml`:

```bash
python dev.py install
```

If dependency installation state looks bad, refresh the persisted stack mounts:

```bash
python dev.py reset-deps
```

Optional host IDE venv (for editor autocomplete, independent from Docker):

```bash
python -m venv .venv_host
.venv_host\Scripts\activate                # Windows
pip install -e ".[dev,ai-eval]"           # optional, local-only tools
```

Container venv remains Linux-native inside docker at `/opt/venv`, while host IDE can use a separate host venv.

### Windows Docker Desktop note

The dev override intentionally masks host-only directories under `/app` with
anonymous volumes:

- `.venv`, `.git`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `.deepeval`
- `agent-transcripts`
- `frontend/node_modules`, `frontend/.next`
- `trading_lab.egg-info`

Do not remove these masks casually. On Windows + Docker Desktop, exposing the
whole repo made the container see ~3 GB of irrelevant host files and made the
unit suite take 15+ minutes. With masks in place, `/app` is ~5.7 MB and the
inner-loop unit suite runs in about a minute.

Use a host venv only for Cursor autocomplete. Runtime dependencies live in the
Docker-native `trading-py-venv` volume, not in the Windows `.venv`.

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
| backend OpenAPI | http://localhost:8000/docs (Swagger UI, themed to match the operator console palette) |
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

## GitHub (maintainers)

This repo is **public**. Branch protection, Actions token defaults, secret
scanning, and fork-safe CI expectations are documented in
[`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) (maintainer checklist included).
