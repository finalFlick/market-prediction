# Decisions Log

Architectural and research decisions, recorded once and not relitigated. Every
decision has an id, date, status, context, decision, and consequences.

Status values: `proposed | accepted | superseded`.

---

## DEC-001 — Strict pipeline architecture

- **Date**: 2026-04-25
- **Status**: accepted
- **Context**: Trading systems decay quickly when research code reaches
  brokers without going through risk, or when execution code starts
  generating signals. We need hard module boundaries from day one.
- **Decision**: Enforce the one-way pipeline
  `data → research → strategies → risk → execution`, with `monitoring`
  cross-cutting. Imports respecting this direction are checked in CI.
- **Consequences**: Simpler reasoning, slower initial development, occasional
  duplication when a feature needs to be lifted into a shared module.

## DEC-002 — Risk engine is non-bypassable

- **Date**: 2026-04-25
- **Status**: accepted
- **Context**: Most production losses on AI-driven trading systems come from
  bypassing risk checks "just for one experiment".
- **Decision**: Every order in every environment (backtest, paper, live)
  passes through `risk.engine.RiskEngine.check_and_size`. There is no
  `skip_risk=True` flag anywhere in the codebase.
- **Consequences**: Backtests that disagree with paper/live are flagged
  immediately because they share the same risk path.

## DEC-003 — Realistic backtest defaults

- **Date**: 2026-04-25
- **Status**: accepted
- **Context**: Naive backtests over-promise; production under-delivers.
- **Decision**: Backtests must include fees, slippage, latency, and (for perps)
  funding. Defaults: 10 bps taker, 2 bps maker, 5 bps slippage, 1-bar fill
  delay, exchange-published funding. Stored in `configs/costs.yaml`.
- **Consequences**: Some signals will look unprofitable that previously looked
  fine. That is the point.

## DEC-004 — Stack: pandas + duckdb + vectorbt + LGBM/XGB/PyTorch

- **Date**: 2026-04-25
- **Status**: accepted
- **Context**: We need fast iteration on tabular features, vectorized
  backtests, and the option to train deep models for sequence data.
- **Decision**:
  - Storage: parquet on disk, DuckDB for ad-hoc queries.
  - Tabular features: pandas + numpy.
  - Backtest engine: vectorbt.
  - Tabular models: LightGBM (default) and XGBoost.
  - Sequence models: PyTorch.
- **Consequences**: We accept vectorbt's design constraints for now; if we
  outgrow them we revisit (custom event-driven engine).

## DEC-005 — Exchanges: Binance + Coinbase first

- **Date**: 2026-04-25
- **Status**: accepted
- **Context**: We need both deep-liquidity perps and a US-regulated venue for
  spot. Future: add Kraken, Bybit, Hyperliquid as needed.
- **Decision**: Initial broker adapters cover Binance (USD-M perps + spot) and
  Coinbase Advanced Trade (spot). Both ship with sandbox/testnet support
  required for paper trading.
- **Consequences**: All adapter abstractions in `execution/brokers/base.py`
  must accommodate both venues' quirks (lot sizes, time-in-force values,
  rate limits).

---

## How to add a decision

1. Pick the next `DEC-NNN` number.
2. Fill in date, status, context, decision, consequences.
3. Reference the `DEC-NNN` id in code comments and PR descriptions where the
   decision is implemented.
