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

## DEC-006 — Live broker registration remains locked in MVP-0

- **Date**: 2026-04-25
- **Status**: accepted
- **Context**: The v1 design requires live adapters to exist for interface
  compatibility while still forbidding runtime registration until explicit
  pre-live gates clear.
- **Decision**: Introduce `execution.brokers.registry.LiveBrokerRegistry` as
  the only registration point. `PaperBroker` registers by default. Live
  adapters (`BinanceLive`, `CoinbaseLive`) raise
  `LiveAdapterRegistrationForbidden` unless `live_adapters_unlocked=true` is
  present in `configs/runtime.yaml` (temporary MVP-0 source of truth).
- **Consequences**: The runner can be written against one broker protocol
  without paper-vs-live branching, while accidental live path activation is
  blocked by default. v1.1 will migrate unlock state to `config_kv` with
  approval-gated workflow.

---

## DEC-007 — Canonical JSON for deterministic artifacts

- **Date**: 2026-04-25
- **Status**: accepted
- **Context**: MVP-0 requires byte-identical `metrics.json` for identical inputs (Invariant 3).
- **Decision**: All metrics and audit payloads use `monitoring.canonical_json` (sorted keys, `Decimal` as string, UTC `Z`, reject NaN/Inf).
- **Consequences**: Writers must not call raw `json.dumps` for `metrics.json` or hash-chain `payload_json` strings.

## DEC-008 — Staggered hash-chained `ha_*` tables

- **Date**: 2026-04-25
- **Status**: accepted
- **Context**: Invariant 4 requires append-only, tamper-evident storage for five critical families.
- **Decision**: `ha_orders`, `ha_fills`, `ha_risk_decisions`, `ha_approvals`, `ha_config_history` in DuckDB; `record_hash = sha256(prev_hash || payload_json)`.
- **Consequences**: Verifier CLI is the source of truth for audit health in `/api/system/health`.

## DEC-009 — OOS-only lever scoring

- **Date**: 2026-04-25
- **Status**: accepted
- **Context**: Req 44.9 / POC 8: no in-sample PnL in learning scores.
- **Decision**: `learning.types.RunSummary` carries only `oos_metrics`; scorers assert non-empty.
- **Consequences**: v1 can add richer calibration without backtesting past leaks.

## How to add a decision

1. Pick the next `DEC-NNN` number.
2. Fill in date, status, context, decision, consequences.
3. Reference the `DEC-NNN` id in code comments and PR descriptions where the
   decision is implemented.
