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

## DEC-010 — Adopt Catppuccin Mocha as the project palette

- **Date**: 2026-04-26
- **Status**: accepted
- **Context**: The hand-built "Kitsune cyberpunk" palette
  (`night/panel/foxfire/mint/lavender/magenta`) was strong on personality
  but weak on engineering: every accent value was hand-tuned, the
  `frontend/styles/tokens.css` referenced in FEATURE-0034 didn't exist,
  contrast/accessibility metadata wasn't recorded, and the API docs
  (`/docs`) had a separate hand-written CSS theme that drifted from the
  dashboard tokens. Maintaining two custom palettes and proving
  cross-surface consistency was lab-internal busywork.
- **Decision**: Adopt **Catppuccin Mocha** (the dark variant of the
  [Catppuccin](https://github.com/catppuccin/catppuccin) design system,
  MIT-licensed, ~19k stars upstream, ports across hundreds of editors /
  CLIs / web tools) as the **single project palette** for both the
  Next.js dashboard and the FastAPI Swagger UI. Hex values come verbatim
  from [`catppuccin/palette`](https://github.com/catppuccin/palette)
  `palette.json` v1.8.0. Tailwind tokens use raw Catppuccin names
  (`base`, `mantle`, `crust`, `surface0/1/2`, `overlay0/1/2`, `text`,
  `subtext0/1`, plus the 14 accents `rosewater` … `lavender`); semantic
  Tailwind utilities (`bg-primary`, `text-success`, etc.) alias to
  Catppuccin's [style-guide role mapping](https://github.com/catppuccin/catppuccin/blob/main/docs/style-guide.md):
  `primary → Blue`, `success → Green`, `warning → Yellow`,
  `danger → Red`, `card → Surface0`, `border → Surface2`,
  `muted-foreground → Subtext0`. Mauve / Teal / Peach reserved for
  AI / live / write accents respectively. The Swagger `/docs` override
  CSS uses the same hex values directly.
- **Consequences**:
  - Removes `night`, `panel`, `foxfire`, `mint`, `magenta` from
    the Tailwind config and from product/spec language.
  - The FEATURE-0034 mood line shifts from "neon telemetry over a
    black-glass trading console" to "quiet operator console with a
    coherent accent vocabulary"; pastel-dark cohesion replaces saturated
    neon. Information density and operator-console intent are
    unchanged.
  - Future dependency-research evaluations (e.g. adding the
    [`@catppuccin/tailwindcss`](https://github.com/catppuccin/tailwindcss)
    plugin) become trivial — the in-repo palette is already aligned.
  - Paused-styleguide-agent WIP on `backup/chore-gov-pre-slim` (commit
    `07d05ab`) defines `frontend/styles/tokens.css` against the old
    Kitsune palette; that branch will need a rebase to land — it does
    not block this decision because it has not been merged.
  - This decision is reversible: every Mocha hex is sourced from a
    single upstream JSON, so swapping to Latte/Frappé/Macchiato or back
    to a custom palette is a one-file change to `tailwind.config.ts`
    plus the Swagger override CSS.

## DEC-011 — Neko Quant brand identity layer (additive to DEC-010)

- **Date**: 2026-04-26
- **Status**: accepted
- **Context**: The operator console needs a light product personality
  (Neko Quant) without forking the palette, trading path, or LLM
  isolation rules. Identity should be swappable, presentation-only, and
  shippable before the full styleguide harness.
- **Decision**: Adopt the **Neko Quant** brand layer: terminal-style
  status (`neko@market`), voice tables, ASCII mascot states, Inter +
  JetBrains Mono, and minimal Swagger `/docs` watermark. Core palette
  remains **Catppuccin Mocha** per DEC-010. All identity code lives in
  `frontend/components/identity/`, `frontend/lib/neko-voice.ts`, and
  `frontend/styles/neko.css` — additive paths that do not replace
  `tokens.css` or the paused styleguide WIP.
- **Consequences**:
  - Product marketing copy in README / UI may use Neko where it does
    not obscure operational data.
  - Mascot / SFX / full terminal mode remain follow-up feature tickets
    (FEATURE-0046–0049) so MVP-0 scope stays honest.

## DEC-012 — Where playful (Neko) copy is allowed

- **Date**: 2026-04-26
- **Status**: accepted
- **Context**: LLM-suggested trade ideas must never be surfaced as
  execution signals ([`.cursor/rules/llm-usage.mdc`](.cursor/rules/llm-usage.mdc),
  `docs/UI_REQUIREMENTS.md`). Playful voice on risk alerts could mask
  real failures.
- **Decision**:
  - **Playful** Neko copy is allowed on: login hero, system overview
    subline, empty list states, diagnostics read-only easter-egg, and
    non-critical loading affordances. Research framing uses
    `NekoObservationCard` with the mandatory line &quot;Research
    observation. Not a trade signal.&quot; when LLM- or model-derived
    text is shown.
  - **Neutral, dense, operational** copy is required for: system health
    KPI tiles, live/PnL and exposure numbers, risk rejects and
    kill-switch status, and any error that blocks the operator.
  - The frontend remains **read-only** for trading; the identity layer
    adds no order placement, kill-switch, or risk bypass UI.
- **Consequences**:
  - Authoring for UI text follows [`.cursor/rules/neko-voice.mdc`](.cursor/rules/neko-voice.mdc).
  - Any future LLM “insight” panel must use the same non-actionable
    disclaimer as `NekoObservationCard`.

## DEC-013 — Spec handoffs and build-time font policy (process)

- **Date**: 2026-04-26
- **Status**: accepted
- **Context**: Shipping FEATURE-0045 additively alongside paused
  FEATURE-0034 showed a gap: no rule required an addendum on the
  sibling spec. Separately, `next/font/google` can fail in restricted
  environments without a documented escape hatch.
- **Decision**:
  1. **Sibling-spec addenda.** When a feature implements code that
     another in-flight or paused spec will need to register (e.g.
     styleguide), append an *Implementation addendum* to that spec
     in `specs/…` per `.cursor/rules/spec-sessions.mdc` and
     `spec-format.mdc` (ticket id consistency in platform task files).
  2. **Offline builds.** Prefer `next/font/local` and vendored
     `.woff2` under `frontend/public/fonts/` when CI cannot reach
     Google Fonts; document in `DECISIONS.md` if vendoring is policy,
     not a one-off.
- **Consequences**: Cursor rules `spec-sessions.mdc`, `spec-format.mdc`,
  and `frontend.mdc` carry the normative text; this decision is the
  project-level record.

## How to add a decision

1. Pick the next `DEC-NNN` number.
2. Fill in date, status, context, decision, consequences.
3. Reference the `DEC-NNN` id in code comments and PR descriptions where the
   decision is implemented.
