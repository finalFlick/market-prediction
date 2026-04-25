# DATA_MODEL

The schema is defined once in [`data/schema.sql`](../data/schema.sql) and
applied on every connection by `data.db.connect()`. Business code accesses
tables through repositories in [`data/repositories/`](../data/repositories);
do not write raw SQL outside that module.

## Tables

### `market_data`  · OHLCV bars

| column         | type         | notes                                  |
|----------------|--------------|----------------------------------------|
| exchange       | VARCHAR      | `binance`, `coinbase`, …               |
| symbol         | VARCHAR      | normalized: `BTCUSDT`, `ETH-USD`       |
| timeframe      | VARCHAR      | `1m`, `5m`, `1h`, `1d`, …              |
| ts             | TIMESTAMPTZ  | bar **open** time, UTC                 |
| open/high/low/close | DOUBLE  |                                        |
| volume         | DOUBLE       | base-currency volume                   |
| quote_volume   | DOUBLE       | quote-currency volume                  |

PK: `(exchange, symbol, timeframe, ts)` — upsert is idempotent.
Repo: `data.OHLCVStore`.

### `signals`  · hypothesis backlog (mirrors `SIGNALS.md`)

| column      | type         |
|-------------|--------------|
| signal_id   | VARCHAR PK   |
| name        | VARCHAR      |
| status      | VARCHAR      | `hypothesis` → `research` → `backtest` → `paper` → `live` → `retired` |
| timeframe   | VARCHAR      |
| intuition   | VARCHAR      |
| owner       | VARCHAR      |
| updated_at  | TIMESTAMPTZ  |

Repo: `data.repositories.SignalsRepo`.

### `strategies`  · registered strategies

| column       | type         |
|--------------|--------------|
| strategy_id  | VARCHAR PK   |
| name         | VARCHAR      |
| universe     | VARCHAR      | comma-joined symbols                   |
| timeframe    | VARCHAR      |
| status       | VARCHAR      | `backtest` / `paper` / `live` / `retired` |
| config_path  | VARCHAR      |
| created_at, updated_at | TIMESTAMPTZ |                              |

Repo: `data.repositories.StrategiesRepo`.

### `trades`  · every fill (backtest, paper, or live)

| column           | type         |
|------------------|--------------|
| trade_id         | VARCHAR PK   |
| client_order_id  | VARCHAR      | idempotency key                        |
| strategy_id      | VARCHAR      | FK → strategies                        |
| exchange, symbol | VARCHAR      |
| side             | VARCHAR      | `buy` / `sell`                         |
| quantity, price, fee, pnl | DOUBLE |                                  |
| venue            | VARCHAR      | `backtest` / `paper` / `live`          |
| ts               | TIMESTAMPTZ  |                                        |

Repo: `data.repositories.TradesRepo`.

### `backtests`  · backtest runs and headline metrics

| column                                              | type         |
|-----------------------------------------------------|--------------|
| run_id                                              | VARCHAR PK   |
| strategy_id                                         | VARCHAR      |
| git_commit, config_hash                             | VARCHAR      |
| started_at, finished_at                             | TIMESTAMPTZ  |
| sharpe, sortino, max_drawdown, cagr, final_equity   | DOUBLE       |
| n_trades                                            | INTEGER      |
| artifact_dir                                        | VARCHAR      |

Repo: `data.repositories.BacktestsRepo`.
Run id format: `<strategy>-<utc>-<commit>-<cfg-hash>`.

## Storage layout

```
data/
  market.duckdb            # all five tables; mounted at /data in containers
  raw/                     # immutable parquet snapshots from ingest
  processed/               # feature matrices, model artifacts
  processed/llm_features/  # per-run LLM-derived feature artifacts (audit)
backtests/
  results/<run_id>/        # manifest.json, equity.parquet, trades.parquet, metrics.json
research/models/registry/<model_id>/   # trained model + manifest.json
```

## Conventions

- **Timestamps are UTC.** Always TIMESTAMPTZ in DuckDB; `pd.Timestamp(tz="UTC")`
  in Python.
- **Symbols are upper-case.** Normalization happens at ingestion.
- **The trading engine is the only writer.** The FastAPI backend is
  read-only; the frontend never touches DuckDB.
