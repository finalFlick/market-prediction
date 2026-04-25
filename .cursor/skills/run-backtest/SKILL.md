---
name: run-backtest
description: Run a deterministic backtest end-to-end and produce the canonical artifact set. Use this skill when the user asks to run, re-run, or smoke-test a backtest, or to validate that determinism holds.
---

# run-backtest

This skill executes a backtest with the project's cost model, walk-forward
splits, and manifest writer — and verifies the run is reproducible.

## When to use

- "Run a backtest on <strategy>" / "smoke the backtest pipeline".
- After a change to `backtests/`, `risk/`, `strategies/`, or `configs/`.
- Before promoting a strategy through the gates in
  [`evaluation.mdc`](mdc:.cursor/rules/evaluation.mdc).

## Inputs

- Strategy module (e.g. `strategies.examples.momentum_xover`).
- Config path under `configs/strategies/<name>.yaml` or `configs/backtest.yaml`.
- Optional: data window override (defaults to config).

## Procedure

1. **Smoke first.** Run `python -m backtests.smoke` and verify it exits 0.
   This is the fast determinism check.
2. **Full run.**
   ```bash
   python -m backtests.run \
       --strategy <module> \
       --config <config-path>
   ```
3. **Verify the manifest.** Open
   `backtests/results/<run_id>/manifest.json` and confirm it has:
   `git_commit`, `config_hash`, `seeds`, `data_window_hash`,
   `library_versions`. Missing field → broken run.
4. **Check determinism.** Re-run the same command. The new
   `metrics.json` must be byte-identical to the previous one (`fc /B`
   on Windows or `diff` elsewhere). If not → file a bug; do not promote.
5. **Read the metrics.** Compare against
   [`docs/EVALUATION.md`](mdc:docs/EVALUATION.md) gates before recommending
   promotion.

## Outputs

- A new directory `backtests/results/<run_id>/` containing
  `manifest.json`, `equity.parquet`, `trades.parquet`, `metrics.json`.
- A new row in `backtests` (DuckDB).
- A 5-bullet summary in the agent response: Sharpe, MaxDD, n_trades,
  hit rate, gate-pass yes/no.

## Forbidden

- Editing `configs/costs.yaml` to make a strategy pass. Cost overrides
  require a `DECISIONS.md` entry.
- Reporting "best of N seeds". Report the median run.
- Marking a strategy ready for paper without re-running determinism.
