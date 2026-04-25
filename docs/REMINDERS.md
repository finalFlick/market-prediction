# Reminders — env keys + dev workflow

This file records two quick reminders you asked for:

## 1) Who reads which env vars

| Variable | Used by | Required? |
|----------|---------|-----------|
| `DUCKDB_PATH`, `DATA_DIR` | Python CLI, backend, engine | Defaults are fine for local work |
| `REDIS_URL` | Backend health check, optional `RedisEventBus` | **Optional** outside Docker: leave empty to use in-memory event bus + DuckDB outbox (`/api/system/health` reports `redis_disabled: true`, `redis_ok: true`) |
| `API_HOST`, `API_PORT` | Uvicorn / backend image | Docker sets these |
| `BINANCE_*`, `COINBASE_*` | Exchange execution / keyed clients | **Only if** you trade or use `--source *-auth` ingesters |
| `BINANCE_PUBLIC_REST_BASE` | `data.ingest.binance_public` | **Optional** — if `api.binance.com` is geo-blocked (HTTP 451), try `https://api.binance.us` (US) |
| `OPERATOR_API_KEY` | Backend kill-switch / operator routes | Set a secret before enabling those routes in prod |
| `OLLAMA_HOST`, `OLLAMA_MODEL` | `research/llm` | Only for LLM features |
| `HERMES_URL` | External “internal helper” (see `AGENTS.md`) | **Not used by MVP-0** — leave empty |
| `NEXT_PUBLIC_API_URL` | Next.js → FastAPI base URL | Required for dashboard data in browser / SSR |
| `NEXTAUTH_URL`, `NEXTAUTH_SECRET` | NextAuth in frontend | Required if you use auth-protected UI |

**Optional install for no-key data:** `pip install 'trading-lab[public-data]'` (pulls `yfinance` for `--source yahoo`).

Helpers:

- `openssl rand -base64 32`
- `python -c "import secrets,base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"`

## 2) Six-step dev workflow (keep this checklist before coding)

1. Analyze the task: restate goal in one sentence, list constraints, define acceptance criteria.
2. Identify files to modify: run `git status`, search symbols, list exact files you will edit.
3. Implement the minimal change: smallest possible diff; avoid drive-by refactors.
4. Run tests: `pytest -q` (and targeted markers as needed).
5. Run lint & typecheck: `ruff check .` and `mypy --strict --explicit-package-bases .`.
6. Validate end-to-end: e.g. `pytest tests/e2e -q`, `python -m backtests.smoke`, `python -m monitoring.audit verify --tables critical`.

Record verification results in `SESSION_LOG.md` when done.

## 3) No-key market data (MVP-0)

```bash
python -m data.ingest.run --source binance --symbol BTCUSDT --timeframe 1h --days 7
python -m data.ingest.run --source coinbase --symbol BTC-USD --timeframe 1h --days 7
python -m data.ingest.run --source yahoo --symbol AAPL --timeframe 1d --days 30
```

Use `--source binance-auth` / `coinbase-auth` only when you wire the keyed CCXT/python clients; those ingesters are still stubs.

**DuckDB vs SQLite:** the app uses **DuckDB** as a single embedded file (like SQLite, no separate server). Swapping to SQLite would be a large schema migration — not needed for “simple.”

**Redis in Docker:** `docker compose up` starts `redis` on `trading-net`; set `REDIS_URL=redis://redis:6379/0` there. Locally without Docker, omit `REDIS_URL`.
