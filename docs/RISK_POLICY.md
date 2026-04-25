# RISK_POLICY

Risk is **non-bypassable**. Every order — backtest, paper, or live — passes
through `risk.engine.RiskEngine.check_and_size`. There is no "skip risk"
flag; CI rejects PRs that introduce one
(see `tests/security/test_risk_engine_non_bypassable.py`).

## Numeric limits (defaults)

Loaded from [`configs/risk.yaml`](../configs/risk.yaml) into
`risk.limits.RiskLimits`. Override per strategy in
`configs/strategies/<name>.yaml`.

| Limit                        | Default | Where checked                          |
|------------------------------|---------|----------------------------------------|
| Max risk per trade           | `1%`    | `risk.sizing.vol_targeted_quantity`    |
| Max daily loss               | `3%`    | `risk.engine.RiskEngine`               |
| Max drawdown (peak-to-trough)| `25%`   | `risk.engine.RiskEngine`               |
| Max gross exposure           | `1.0×`  | `risk.engine.RiskEngine`               |
| Max leverage                 | `1.0×`  | `risk.engine.RiskEngine`               |
| Max per-symbol weight        | `25%`   | `risk.engine.RiskEngine`               |
| Min order notional           | exchange-specific | `risk.sizing.clip_quantity_to_min_notional` |

Crossing any limit rejects the order with a `RiskCheckRejected` carrying
the rule name; the rejection is logged via `monitoring.logger`.

## Promotion gates

| Stage      | Gate                                                                |
|------------|---------------------------------------------------------------------|
| `backtest` | meets thresholds in [`EVALUATION.md`](EVALUATION.md)                |
| `paper`    | RiskAgent reviewed exposure / DD; capped at the strategy's `paper_capital` |
| `live`     | ≥ 14 consecutive paper days within tolerance + RiskAgent sign-off in [`DECISIONS.md`](../DECISIONS.md) |
| `retired`  | kill-switch tripped or postmortem filed                             |

## Kill-switch

`monitoring.drift.detect_drift` compares realized vs backtest distributions.
Crossing the configured z-threshold:

1. Sets the engine's `kill_switch=True`.
2. Cancels open orders via the active broker.
3. Marks the strategy `retired` in the `strategies` table.
4. Files an alert and a `DECISIONS.md` entry.

Resuming a killed strategy requires a human reviewer.

## Code review trigger

Any PR touching `risk/`, `execution/`, or `configs/risk.yaml` requires:

- Human review (no agent-only merges).
- A passing run from `tests/strategy/` and `tests/e2e/` cited in the PR
  description.
- Updated entries in `DECISIONS.md` if a default limit changes.

## What never lands

- `skip_risk`, `bypass_risk`, `RISK_BYPASS`, `DISABLE_RISK` flags.
- LLM-generated trade decisions (LLMs are research-only — see
  [`.cursor/rules/llm-usage.mdc`](../.cursor/rules/llm-usage.mdc)).
- Hardcoded position sizes in strategy code.
- Live orders without a recorded `client_order_id` (idempotency requirement).
