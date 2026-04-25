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
