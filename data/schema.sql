-- DuckDB schema for trading-lab. Applied at boot by `data.db.connect()`.
-- All timestamps are TIMESTAMPTZ in UTC. Symbols are upper-case strings.

CREATE TABLE IF NOT EXISTS market_data (
    exchange      VARCHAR     NOT NULL,
    symbol        VARCHAR     NOT NULL,
    timeframe     VARCHAR     NOT NULL,
    ts            TIMESTAMPTZ NOT NULL,
    open          DOUBLE      NOT NULL,
    high          DOUBLE      NOT NULL,
    low           DOUBLE      NOT NULL,
    close         DOUBLE      NOT NULL,
    volume        DOUBLE      NOT NULL,
    quote_volume  DOUBLE      NOT NULL,
    PRIMARY KEY (exchange, symbol, timeframe, ts)
);

CREATE INDEX IF NOT EXISTS market_data_symbol_ts ON market_data (symbol, ts);

CREATE TABLE IF NOT EXISTS signals (
    signal_id     VARCHAR     NOT NULL,   -- e.g. SIG-001
    name          VARCHAR     NOT NULL,
    status        VARCHAR     NOT NULL,   -- hypothesis|research|backtest|paper|live|retired
    timeframe     VARCHAR     NOT NULL,
    intuition     VARCHAR,
    owner         VARCHAR,
    updated_at    TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (signal_id)
);

CREATE TABLE IF NOT EXISTS strategies (
    strategy_id   VARCHAR     NOT NULL,   -- short slug, e.g. momentum_xover
    name          VARCHAR     NOT NULL,
    universe      VARCHAR     NOT NULL,   -- comma-joined symbols
    timeframe     VARCHAR     NOT NULL,
    status        VARCHAR     NOT NULL,   -- backtest|paper|live|retired
    config_path   VARCHAR,
    created_at    TIMESTAMPTZ NOT NULL,
    updated_at    TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (strategy_id)
);

CREATE TABLE IF NOT EXISTS trades (
    trade_id        VARCHAR     NOT NULL,
    client_order_id VARCHAR     NOT NULL,
    strategy_id     VARCHAR,
    exchange        VARCHAR     NOT NULL,
    symbol          VARCHAR     NOT NULL,
    side            VARCHAR     NOT NULL,
    quantity        DOUBLE      NOT NULL,
    price           DOUBLE      NOT NULL,
    fee             DOUBLE      NOT NULL DEFAULT 0,
    pnl             DOUBLE,
    venue           VARCHAR     NOT NULL, -- backtest|paper|live
    ts              TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (trade_id)
);

CREATE INDEX IF NOT EXISTS trades_strategy_ts ON trades (strategy_id, ts);
CREATE INDEX IF NOT EXISTS trades_symbol_ts   ON trades (symbol, ts);

CREATE TABLE IF NOT EXISTS backtests (
    run_id        VARCHAR     NOT NULL,   -- <strategy>-<utc>-<commit>-<cfg-hash>
    strategy_id   VARCHAR     NOT NULL,
    git_commit    VARCHAR,
    config_hash   VARCHAR,
    started_at    TIMESTAMPTZ NOT NULL,
    finished_at   TIMESTAMPTZ,
    sharpe        DOUBLE,
    sortino       DOUBLE,
    max_drawdown  DOUBLE,
    cagr          DOUBLE,
    final_equity  DOUBLE,
    n_trades      INTEGER,
    artifact_dir  VARCHAR     NOT NULL,
    PRIMARY KEY (run_id)
);

CREATE INDEX IF NOT EXISTS backtests_strategy ON backtests (strategy_id, started_at);

-- Hash-chained audit (Day-0 Invariant 4). Per-table chain; genesis prev_hash = 64 zero bytes as hex.
CREATE TABLE IF NOT EXISTS ha_orders (
  seq            BIGINT       PRIMARY KEY,
  natural_key    VARCHAR      NOT NULL,
  run_id         VARCHAR,
  payload_json   VARCHAR      NOT NULL,
  prev_hash      CHAR(64)     NOT NULL,
  record_hash    CHAR(64)     NOT NULL,
  created_at     TIMESTAMPTZ  NOT NULL
);

CREATE TABLE IF NOT EXISTS ha_fills (
  seq            BIGINT       PRIMARY KEY,
  natural_key    VARCHAR      NOT NULL,
  run_id         VARCHAR,
  payload_json   VARCHAR      NOT NULL,
  prev_hash      CHAR(64)     NOT NULL,
  record_hash    CHAR(64)     NOT NULL,
  created_at     TIMESTAMPTZ  NOT NULL
);

CREATE TABLE IF NOT EXISTS ha_risk_decisions (
  seq            BIGINT       PRIMARY KEY,
  natural_key    VARCHAR      NOT NULL,
  run_id         VARCHAR,
  payload_json   VARCHAR      NOT NULL,
  prev_hash      CHAR(64)     NOT NULL,
  record_hash    CHAR(64)     NOT NULL,
  created_at     TIMESTAMPTZ  NOT NULL
);

CREATE TABLE IF NOT EXISTS ha_approvals (
  seq            BIGINT       PRIMARY KEY,
  natural_key    VARCHAR      NOT NULL,
  run_id         VARCHAR,
  payload_json   VARCHAR      NOT NULL,
  prev_hash      CHAR(64)     NOT NULL,
  record_hash    CHAR(64)     NOT NULL,
  created_at     TIMESTAMPTZ  NOT NULL
);

CREATE TABLE IF NOT EXISTS ha_config_history (
  seq            BIGINT       PRIMARY KEY,
  natural_key    VARCHAR      NOT NULL,
  run_id         VARCHAR,
  payload_json   VARCHAR      NOT NULL,
  prev_hash      CHAR(64)     NOT NULL,
  record_hash    CHAR(64)     NOT NULL,
  created_at     TIMESTAMPTZ  NOT NULL
);

-- Run engine (MVP-0) — `state_transitions` is append-only; not hash-chained at MVP-0.
CREATE TABLE IF NOT EXISTS runs (
  run_id         VARCHAR     NOT NULL PRIMARY KEY,
  parent_run_id  VARCHAR,
  experiment_id  VARCHAR,
  run_type       VARCHAR     NOT NULL,   -- backtest|paper|strategy_test
  mode           VARCHAR     NOT NULL,   -- backtest|paper|live|dry_run
  status         VARCHAR     NOT NULL,   -- queued|running|paused|completed|failed|cancelled
  config_json    VARCHAR     NOT NULL,   -- frozen RunConfig JSON
  config_hash    VARCHAR     NOT NULL,
  git_commit     VARCHAR     NOT NULL,
  artifact_dir   VARCHAR,
  error_reason   VARCHAR,
  started_at     TIMESTAMPTZ,
  finished_at    TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS experiments (
  experiment_id  VARCHAR     NOT NULL PRIMARY KEY,
  run_type       VARCHAR     NOT NULL,
  started_at     TIMESTAMPTZ NOT NULL,
  last_run_id    VARCHAR
);

CREATE TABLE IF NOT EXISTS state_transitions (
  st_id          VARCHAR     NOT NULL PRIMARY KEY,
  run_id         VARCHAR     NOT NULL,
  from_status    VARCHAR,
  to_status      VARCHAR     NOT NULL,
  reason         VARCHAR     NOT NULL,
  actor          VARCHAR     NOT NULL,
  transitioned_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS run_events_durable (
  stream         VARCHAR     NOT NULL,
  event_id       VARCHAR     NOT NULL,
  natural_key    VARCHAR     NOT NULL,
  payload_json   VARCHAR     NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (stream, event_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS run_events_dedup ON run_events_durable (stream, natural_key);

-- YAML → DuckDB seed (MVP-0 read model)
CREATE TABLE IF NOT EXISTS config_kv (
  scope          VARCHAR     NOT NULL,
  key            VARCHAR     NOT NULL,
  value_json     VARCHAR     NOT NULL,
  updated_at     TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (scope, key)
);

-- Lever scoreboard (MVP-0 foundation)
CREATE TABLE IF NOT EXISTS scoreboard (
  level          VARCHAR     NOT NULL,   -- strategy|source|feature|llm_calibration
  key            VARCHAR     NOT NULL,
  score          DOUBLE      NOT NULL,
  weight         DOUBLE      NOT NULL DEFAULT 1.0,
  last_run_id    VARCHAR,
  updated_at     TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (level, key)
);
