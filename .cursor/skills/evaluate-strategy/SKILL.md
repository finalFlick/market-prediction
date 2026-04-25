---
name: evaluate-strategy
description: Score a backtest against the project's acceptance gates and decide whether it qualifies for paper trading. Use this skill when the user asks "is this strategy good enough?" or "did it pass the gates?"
---

# evaluate-strategy

This skill scores a completed backtest against the gates in
[`docs/EVALUATION.md`](mdc:docs/EVALUATION.md) and produces a clear
pass / fail recommendation.

## When to use

- After [`run-backtest`](mdc:.cursor/skills/run-backtest/SKILL.md) completes.
- When reviewing a candidate for promotion `backtest → paper`.

## Inputs

- A `run_id` (from the `backtests` table) **or** a path to
  `backtests/results/<run_id>/metrics.json`.

## Procedure

1. Load the metrics:
   ```python
   from data import BacktestsRepo
   from data.db import connect
   row = BacktestsRepo(connect()).get(run_id)
   ```
2. Score each gate:

   | Gate            | Threshold             | Field              |
   |-----------------|-----------------------|--------------------|
   | Sharpe          | > 1.0                 | `row.sharpe`       |
   | Max drawdown    | > -0.25 (DD < 25%)    | `row.max_drawdown` |
   | n_trades        | >= 50                 | `row.n_trades`     |
   | CAGR            | > 0 and > buy-and-hold| `row.cagr`         |
   | Hit rate        | >= 0.45               | from `trades.parquet` |

3. Run walk-forward sanity: are out-of-fold metrics within ±25% of the
   in-sample summary? If `research/cv.py` produced fold metrics, load and
   check; otherwise mark "walk-forward not run".
4. Check leakage: confirm `assert_no_lookahead` passes on the feature
   pipeline used by this strategy.
5. Produce a verdict:
   - **PASS** → ready for `promote-strategy` (`backtest → paper`).
   - **PARTIAL** → list which gates failed and by how much.
   - **FAIL** → recommend ablations, not re-tuning.

## Outputs

- A markdown table with each gate, the value, the threshold, pass/fail.
- A verdict line: `PASS`, `PARTIAL`, or `FAIL`.
- If PASS, an explicit instruction to invoke `promote-strategy`.

## Forbidden

- Lowering a gate to make a strategy pass. The gates are policy.
- Ignoring failed walk-forward sanity checks. Regime fragility is real.
- Recommending `live` from this skill — that needs paper-trading data
  and `RiskAgent` sign-off in `DECISIONS.md`.
