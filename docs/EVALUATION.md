# EVALUATION

Acceptance rules for promoting a strategy through `backtest → paper → live`.
Targets are baselines; `RiskAgent` may tighten them per-strategy. Source for
metric definitions: [`backtests/metrics.py`](../backtests/metrics.py).

## Strategy acceptance gates

A strategy may advance to `paper` only if its qualifying backtest meets
**all** of the following on out-of-sample data:

| Metric                | Threshold                              |
|-----------------------|----------------------------------------|
| Sharpe (annualized)   | `> 1.0`                                |
| Max drawdown          | `< 25%` (i.e. `> -0.25`)               |
| CAGR                  | `> 0` and beats buy-and-hold in OOS    |
| Trade count           | `>= 50` over the test window           |
| Hit rate              | `>= 0.45`                              |
| Turnover              | reasonable for the timeframe (Sharpe net of fees still passes) |

A strategy may advance to `live` only if **also**:

- Walk-forward / purged k-fold metrics are within ±25% of the in-sample
  summary (no clear regime over-fit).
- It has produced ≥ 14 consecutive paper-trading days within the same
  tolerance band.
- `RiskAgent` has reviewed exposure, drawdown, and tail-risk numbers and
  signed off in [`DECISIONS.md`](../DECISIONS.md).

## Backtest validity

A backtest is valid only if:

- Costs (fees, slippage, latency) come from `configs/costs.yaml`. Overrides
  are logged in the run manifest and require a `DECISIONS.md` entry.
- Look-ahead is impossible (`assert_no_lookahead` runs as part of the test).
- The data window is a versioned snapshot (DuckDB or parquet hash recorded
  in the manifest).
- Re-running the same config produces byte-identical `metrics.json`. CI
  enforces this on a fixture.

See [`.cursor/rules/backtesting.mdc`](../.cursor/rules/backtesting.mdc) for
the full list of forbidden patterns and required artifacts.

## AI / LLM output evaluation

LLM-generated text that influences a research artifact is regression-tested
in [`ai_evals/`](../ai_evals/). See
[`ai_evals/EVAL_GUIDELINES.md`](../ai_evals/EVAL_GUIDELINES.md).

## When a strategy fails

- Failing in backtest → ablate (reduce features, simpler model). Do not
  re-tune on the same window — that's leakage.
- Failing in paper → revert status to `backtest`. `MonitoringAgent` files an
  issue with the realized vs expected diff.
- Failing in live → kill-switch trips automatically; status drops to
  `retired` and a postmortem lands in `DECISIONS.md`.
