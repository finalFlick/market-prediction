---
name: promote-strategy
description: Advance a strategy through the lifecycle (backtest → paper → live → retired) with the required artifacts. Use this skill when the user asks to promote, paper-trade, or retire a strategy.
---

# promote-strategy

This skill advances a strategy's `status` field with the required gates.
Each step requires evidence — the skill refuses to promote without it.

## When to use

- "Move <strategy> to paper" / "graduate to live" / "retire <strategy>".

## Inputs

- `strategy_id`.
- Target status: `paper`, `live`, or `retired`.
- For `paper`: the `run_id` of the qualifying backtest.
- For `live`: paper-trading window summary + `RiskAgent` review note.

## Procedure

### To paper (from backtest)

1. Confirm `evaluate-strategy` returned PASS for the cited `run_id`.
2. Update `strategies.status = 'paper'`:
   ```python
   from data.repositories import StrategiesRepo
   from data.db import connect
   StrategiesRepo(connect()).upsert(strategy_record._replace(status="paper"))
   ```
3. Append a `DECISIONS.md` entry: ID, date, gate values, paper capital cap.
4. Cap paper capital in `configs/strategies/<name>.yaml`.

### To live (from paper)

1. Verify ≥ 14 paper-trading days within ±25% of in-sample.
2. Verify `RiskAgent` sign-off appears in `DECISIONS.md` (search the file).
3. Update `strategies.status = 'live'`.
4. Append a `DECISIONS.md` entry citing both the qualifying backtest and
   the paper-trading window.

### To retired (any source)

1. Update `strategies.status = 'retired'`.
2. Cancel any open orders for the strategy via the active broker.
3. Append a postmortem to `DECISIONS.md` with the trigger (kill-switch,
   manual, drift, etc.) and lessons learned.

## Outputs

- A row update in `strategies`.
- A new `DECISIONS.md` entry.
- A confirmation summary in the response: old status → new status, with
  the qualifying evidence cited.

## Forbidden

- Promoting to `live` without the explicit `RiskAgent` sign-off in
  `DECISIONS.md`. CI cannot make this decision.
- Skipping the `DECISIONS.md` entry. The audit trail is non-negotiable.
- Editing `configs/risk.yaml` defaults as part of promotion — those are
  global, not per-strategy.
