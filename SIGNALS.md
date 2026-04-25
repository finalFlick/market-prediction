# Signals Backlog

The single source of truth for trading-signal hypotheses and their lifecycle.

| ID       | Name                  | Intuition                                                             | Timeframe | Horizon | Status     | Owner           | Run ids |
|----------|-----------------------|-----------------------------------------------------------------------|-----------|---------|------------|-----------------|---------|
| SIG-001  | Momentum crossover    | Short-term price persists; fast/slow EMA crossover catches trend.      | 1h        | 4–24h   | hypothesis | SignalAgent     |         |
| SIG-002  | Mean reversion z-score| Cross-sectional dollar-vol-weighted return z deviates and reverts.    | 1h        | 1–8h    | hypothesis | ResearchAgent   |         |
| SIG-003  | Funding-rate carry    | Persistently positive perp funding penalizes longs; short the rate.   | 8h        | 1–7d    | hypothesis | ResearchAgent   |         |

Status values: `hypothesis | research | backtest | paper | live | retired`.

---

## How to add a signal

1. Pick the next `SIG-NNN`.
2. Fill: name, intuition (1–2 sentences), timeframe, expected horizon.
3. Add **falsification criteria** below — the metrics threshold that must hold
   for the signal to keep advancing.
4. As the signal advances, append `Run ids` from `backtests/results/`.

## Falsification criteria

- **SIG-001 Momentum crossover**
  - In-sample net Sharpe > 1.0 after default cost model on BTCUSDT 1h, 2 yrs.
  - Walk-forward Sharpe > 0.7 on the last 12 months.
  - Max drawdown < 25%.
- **SIG-002 Mean reversion z-score**
  - Net Sharpe > 0.8 on a top-20 spot universe.
  - Turnover-adjusted return > buy-and-hold.
  - Hit rate > 52% on closed trades.
- **SIG-003 Funding-rate carry**
  - Net carry-only Sharpe > 1.5 across BTC/ETH perps.
  - Tail loss in 99th-percentile crash week < 2× weekly std.
