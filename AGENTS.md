# AGENTS.md

This document defines the AI agents that collaborate on `trading-lab` and the
workflow that connects them. Each agent owns one stage of the pipeline and
hands off typed artifacts to the next stage.

```
ResearchAgent → SignalAgent → BacktestAgent → StrategyAgent
              → RiskAgent → ExecutionAgent → MonitoringAgent
```

## Quick reference

| Agent             | One-line responsibility                                   |
|-------------------|-----------------------------------------------------------|
| `ResearchAgent`   | Discover signals from research papers and market context  |
| `SignalAgent`     | Implement signal features and train baseline models       |
| `BacktestAgent`   | Run vectorbt simulations with realistic costs             |
| `StrategyAgent`   | Combine signals into trading strategies                   |
| `RiskAgent`       | Apply position sizing and stop rules; gate promotions     |
| `ExecutionAgent`  | Place trades via CCXT and reconcile fills                 |
| `MonitoringAgent` | Track system health, drift, and PnL vs expectation        |

Every agent reads the `.cursor/rules/` files. Cross-cutting expectations live
there; per-agent details live below.

---

## ResearchAgent

**Owns:** market understanding, hypothesis generation, data inventory.

**Responsibilities**
- Survey market microstructure, asset classes, and recent literature.
- Maintain `SIGNALS.md` as a backlog of testable hypotheses.
- Specify data requirements (symbols, timeframes, history depth) and request
  ingestion from the data layer.
- Define labels and prediction horizons in `research/labels.py`.

**Inputs:** market questions, news, prior `DECISIONS.md` entries.
**Outputs:** new `SIGNALS.md` rows, label definitions, data-pull requests.
**Hands off to:** `SignalAgent`.

---

## SignalAgent

**Owns:** turning hypotheses into reproducible numerical signals.

**Responsibilities**
- Implement features in `research/features/` as point-in-time pure functions.
- Train baseline + candidate models (`lightgbm`, `xgboost`, `pytorch`).
- Maintain the model registry under `research/models/registry/`.
- Report feature importance, calibration, and information coefficient (IC).

**Inputs:** hypothesis from `ResearchAgent`, OHLCV / order book data.
**Outputs:** trained model artifact + `manifest.json`, signal scoring function.
**Hands off to:** `BacktestAgent`.

**Hard rules**
- No look-ahead. Validate with the shift-check utility in
  `research/features/validation.py`.
- Walk-forward or purged k-fold with embargo. No naive train/test split.

---

## BacktestAgent

**Owns:** turning a model into an honest performance estimate.

**Responsibilities**
- Wrap a signal in a strategy spec and run `backtests/run.py`.
- Apply the project default cost model (`configs/costs.yaml`) unless explicitly
  overridden in `DECISIONS.md`.
- Produce the standard artifact set defined in `.cursor/rules/backtesting.mdc`.
- Compare results against benchmarks (buy-and-hold, equal-weight).

**Inputs:** trained model from `SignalAgent`.
**Outputs:** run id under `backtests/results/`, summary in PR description.
**Hands off to:** `StrategyAgent` (if metrics pass thresholds) or back to
`SignalAgent` (if not).

---

## StrategyAgent

**Owns:** composing one or more signals into a complete trading strategy.

**Responsibilities**
- Define entry, exit, holding period, and rebalancing rules in `strategies/`.
- Combine multiple signals with a documented blending policy
  (rank-blend, regime gating, hierarchical risk-parity, etc.).
- Specify the symbol universe and rebalance schedule.
- Re-run `BacktestAgent` on the composed strategy and ensure it still passes.

**Inputs:** validated signals from `BacktestAgent`.
**Outputs:** strategy module + config in `configs/strategies/`.
**Hands off to:** `RiskAgent`.

---

## RiskAgent

**Owns:** the *only* path through which orders reach the market.

**Responsibilities**
- Implement and maintain `risk/engine.py` checks: max gross exposure, max per-
  symbol weight, max leverage, max daily loss, drawdown stop, kill-switch.
- Convert target weights to safe order quantities via volatility-targeted
  sizing (`risk/sizing.py`).
- Reject orders that violate any rule and log the rejection reason.
- Approve `paper → live` promotions based on backtest, paper-trading, and
  exposure analysis.

**Inputs:** strategy target positions / orders.
**Outputs:** risk-adjusted orders, rejection events, promotion decisions.
**Hands off to:** `ExecutionAgent`.

**Hard rules**
- The risk engine is **non-bypassable**. There is no "skip risk" flag in any
  environment, including backtests.
- Limits are sourced from `configs/risk.yaml`, never hardcoded in strategies.

---

## ExecutionAgent

**Owns:** placing orders and reconciling state with the exchange.

**Responsibilities**
- Implement broker adapters in `execution/brokers/` (paper, Binance, Coinbase).
- Handle order lifecycle: place, monitor, cancel, modify, reconcile fills.
- Maintain a local view of positions, PnL, and open orders, and reconcile
  against exchange truth on every event.
- Surface execution quality metrics (slippage vs decision price, fill rate).

**Inputs:** approved orders from `RiskAgent`.
**Outputs:** fills, position state, execution-quality reports.
**Hands off to:** `MonitoringAgent`.

**Hard rules**
- Idempotent order placement keyed by client order id.
- Exchange API keys are loaded only via env vars; never logged.

---

## MonitoringAgent

**Owns:** observability, drift detection, and alerts.

**Responsibilities**
- Provide structured logging via `monitoring/logger.py` for all modules.
- Track live PnL vs backtest expectation; alert on drift beyond N sigma.
- Track feature drift, model staleness, and broker connectivity.
- Trigger the kill-switch when monitored thresholds are breached.

**Inputs:** events from every other module.
**Outputs:** logs, metrics, alerts, kill-switch signals.
**Hands off to:** humans (and the next research cycle).

---

## Workflow

A typical research-to-production loop:

```
ResearchAgent     opens SIGNAL-NN in SIGNALS.md
        ↓
SignalAgent       implements feature + label + model;  status: research
        ↓
BacktestAgent     runs honest backtest;                status: backtest
        ↓ (passes thresholds)
StrategyAgent     composes into strategies/<name>.py
        ↓
RiskAgent         reviews exposure, sets per-strategy limits
        ↓
ExecutionAgent    runs in paper for ≥ N days;          status: paper
        ↓ (RiskAgent approves)
ExecutionAgent    deploys with capped capital;         status: live
        ↓
MonitoringAgent   continuously verifies; can revert any stage
```

Every transition writes a row to `DECISIONS.md` and updates the signal's row
in `SIGNALS.md`.

---

## LLM usage policy

LLMs (local Ollama models) are research assistants for `ResearchAgent`,
`SignalAgent`, and `StrategyAgent`. They are NEVER on the trading path.

| Agent             | LLM allowed? | Notes                                                    |
|-------------------|:------------:|----------------------------------------------------------|
| `ResearchAgent`   | yes          | Hypothesis generation, news summarization                |
| `SignalAgent`     | yes          | Naming features, sketching transformations               |
| `BacktestAgent`   | yes          | Plain-language report on a *finished* backtest           |
| `StrategyAgent`   | yes          | Composer rationale; never produces a target weight       |
| `RiskAgent`       | **no**       | Limits and approvals are deterministic                   |
| `ExecutionAgent`  | **no**       | No LLM in the order path                                 |
| `MonitoringAgent` | yes          | Annotates alerts in plain language; cannot trigger them  |

The LLM client lives at `research/llm/client.py`. CI runs
`tests/security/test_llm_isolation.py` to prove no module under `execution/`
imports `research.llm` (transitively or otherwise). See
`.cursor/rules/llm-usage.mdc` for the full policy.

---

## Service topology (prod)

The full system runs as containers on the `trading-net` docker network:

| Container        | Owned by              | Notes                                          |
|------------------|-----------------------|------------------------------------------------|
| `frontend`       | dashboard             | Next.js, reads `backend` only                  |
| `backend`        | read-only API         | FastAPI, reads DuckDB + Redis                  |
| `trading-engine` | live + paper trading  | Strategy → Risk → Execution loop               |
| `redis`          | pub/sub               | Connects engine, backend, monitoring           |
| `duckdb`         | shared volume         | Holds market_data, signals, trades, strategies, backtests tables |
| `ollama`         | external              | LLM runtime, used by `research/llm/`           |
| `hermes`         | external              | Internal helper                                |

See `.cursor/rules/deployment.mdc` for service-level rules.
