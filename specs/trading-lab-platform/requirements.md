# Requirements: trading-lab-platform

## Document Information

- **Feature Name**: trading-lab-platform
- **Version**: 0.1
- **Date**: 2026-04-25
- **Author**: Brandon
- **Stakeholders**: Brandon (sole operator)
- **Related Documents**:
  - Design: `./design.md`
  - Tasks: `./tasks.md`
  - Project rules: `.cursor/rules/architecture.mdc`, `risk-management.mdc`, `security.mdc`, `llm-usage.mdc`, `spec-sessions.mdc`
  - Existing scaffold contracts: `AGENTS.md`, `DECISIONS.md`, `SIGNALS.md`, `docs/ARCHITECTURE.md`, `docs/DESIGN.md`

## Introduction

This spec defines v1 of the trading-lab platform: a self-hosted, run-loop based,
self-improving market-intelligence and paper-trading system that monitors broad
markets, generates predictions, simulates trades through a deterministic risk
engine, logs every decision with full reasoning context, summarizes each run with
an LLM, and proposes config / strategy / universe deltas for the next run. The
operator approves changes through the dashboard; the system never auto-flips
live mode.

The v1 perimeter is intentionally narrow on execution (crypto spot via
Binance/Coinbase, US equities/ETFs via Alpaca paper, Schwab read-only) and broad
on monitoring (price, news/RSS, manual paste-in MUST in v1; X, YouTube, on-chain,
Reddit, earnings allowed-later). All configuration is editable from the
dashboard; YAML files are an import/export format, not a maintenance activity.

### Feature Summary

A self-hosted, run-loop based market-intelligence and paper-trading platform
with strict, non-bypassable risk gating, a dashboard LLM chat surface, and an
evidence-driven strategy promotion ladder.

### Business Value

- **Avoids overfitting and account wipeout** by forcing every order through
  `risk.engine.RiskEngine.check_and_size` (per `.cursor/rules/risk-management.mdc`)
  and gating live capital at $1,000.
- **Compounds learning across runs** via an MLflow-style experiment registry,
  so the platform improves week over week without manual config tuning.
- **Surfaces a unified picture of all markets the operator cares about** —
  crypto, equities, Schwab portfolio — in one dashboard with one LLM chat.
- **Stays free and self-hosted**, so monthly cost is bounded by hardware, not
  subscriptions.

### Scope

- **In scope**: market data ingest (crypto + equities), news/RSS ingest, manual
  insight intake, run engine (4 run types), strategy library + R-ladder
  promotion, risk engine + kill switch, paper trading via internal `PaperBroker`
  and Alpaca paper, Schwab read-only integration with LLM analysis, dashboard
  with realtime run view, multi-provider LLM layer (Ollama / OpenAI / Anthropic),
  notification system (UI / Discord / Email), full audit logging, deterministic
  backtesting with reproducibility manifests, MLflow-style experiment tracking,
  Docker-Compose deployment on Unraid.
- **Out of scope (v1)**: mobile native app; multi-user / per-user accounts;
  public sharing of runs/strategies; cloud deployment; tax-lot tracking and
  1099-B export; options trading; HFT (sub-second latency); online-updating
  reinforcement-learning agents; auto-flipping live mode; fully autonomous live
  trading without manual enable; paid SaaS dependencies; 3rd-party strategy
  marketplaces; X/Twitter automated ingest (deferred to v2); voice or CLI chat
  surfaces (Cursor MCP and Discord bot deferred).

### Guiding Principles

Every requirement in this document MUST be read against the following 26
cross-cutting principles. They are the lens through which design, tasks, and
implementation are evaluated. Where a principle clashes with a specific
requirement, the principle wins unless the requirement cites a `DECISIONS.md`
entry explaining the deviation.

**North-star**

1. **Singular goal: learn to make money over time.** Every subsystem,
   feature, and metric must ultimately serve this. If a feature does not
   plausibly improve the platform's ability to find or exploit edges, it
   does not ship in v1.

**Behavior**

2. **Fully configurable.** Every operational knob is editable through the
   dashboard UI (Requirement 33).
3. **Learning across all possible levers, always.** Sources, features,
   strategies, models, universe, LLM calibration, parameters, slippage
   estimates, alert thresholds, decision cadence, prompt versions — all
   scored, persisted, and adapted (Requirement 44).
4. **Continuous growth over time.** The platform's effectiveness compounds
   across runs via approved global memory (Requirement 8) and the R-ladder
   (Requirements 13, 14).
5. **Dynamic and flexible.** Schemas, registries, and interfaces accept new
   sources, features, strategies, run types, and brokers without engine
   rewrites.
6. **Robust.** Every external boundary has retries, circuit breakers, and
   stale-data detection (Reliability + Resilience non-functional).
7. **Simple.** KISS: prefer the smallest design that satisfies the
   requirement; reject incidental complexity (Requirement 47).
8. **Clear and accurate.** Logs, metrics, summaries, and UI copy are
   precise; vague adjectives are forbidden in artifacts (Requirements 36,
   41, 42).
9. **Useful.** Every feature ties to a measurable improvement in run
   outcomes, observability, or operator action time.

**UI / UX**

10. **Excellent, modern UI/UX.** Next.js 14 + Tailwind + shadcn-style
    components; consistent design system; component-first delivery via the
    `/styleguide` page; accessibility-aware (Requirements 33, 34, 35, 50).
11. **Built-in AI is a core feature.** The dashboard chat, run
    retrospective, and Insight Intake are first-class subsystems
    (Requirements 16, 18, 21, 22).
12. **Excellent, complete dashboards.** Every run type, every R-ladder
    state, every alert, every Schwab view, every config knob, and every
    diagnostic surface has a dashboard view (Requirements 33, 36, 41).
13. **Responsive.** Sub-1.5s page loads, sub-500ms p95 run-event push
    (Performance non-functional).

**Quality**

14. **Quality tests over quantity.** Aim coverage at key components and
    tools; every test asserts observable behavior; no coverage-only tests
    (Requirements 26, 46.5–46.8, 46.11, 50.7, Definition of Done).
15. **It works.** Definition of Done forbids "should work" / "left as an
    exercise" / `partial` without explicit waiver (per
    `.cursor/rules/pr-review.mdc`).
16. **Stable and secure.** Security non-functional + Reliability
    non-functional; gitleaks + LLM-isolation tests in CI (Requirement 23,
    Security non-functional).
17. **Fast — and self-aware when it isn't.** The system tracks its own
    latency / throughput / cost and surfaces regressions (Requirement 45).
18. **Excellent notifications and reporting.** Three severities, three
    channels, the seven canonical alerts wired and tested (Requirements 31,
    32).
19. **Production-grade.** No TODOs, no stubs, no placeholder returns, no
    commented-out code in shipped releases (Requirement 46).
20. **No shortcuts in design or implementation.** If a corner is being
    cut, mark the work `partial` and write a `DECISIONS.md` entry; do not
    paper over (Requirement 46).

**Engineering process**

21. **Modular components, library-first.** Prefer well-maintained packages
    and MCP servers over custom code; every UI component is reusable,
    documented in the styleguide, and demoable in isolation. Custom code
    requires `DECISIONS.md` justification (Requirements 47, 50).
22. **Always research the web.** Implementation tasks consult current
    docs, GitHub issues, and proven patterns before writing code
    (Requirement 48).
23. **Always use Cursor tools and MCPs.** Use `.cursor/agents/`,
    `.cursor/skills/`, `.cursor/hooks/`, `.cursor/mcp.json` servers, and
    the Cursor harness on every implementation task (Requirement 49).
24. **Always get latest docs and information.** Web research output
    references the date and source; stale guidance is rejected
    (Requirement 48).
25. **Never rebuild what exists.** If a proven approach, library, or MCP
    already solves the problem, use it. Reinvention requires
    `DECISIONS.md` justification (Requirement 47).

**Governance**

26. **The 25 principles above are non-negotiable.** Tasks that violate
    them are rejected at PR review per `.cursor/rules/pr-review.mdc`.

---

## Phasing

After the design review on 2026-04-25, requirements are tagged with a
**phase** so that `tasks.md` can be aggressively sliced without losing
scope. **Nothing has been removed.** Items not in MVP-0 are preserved
verbatim under a later phase tag.

| Phase | Meaning |
|---|---|
| `[MVP-0]` | First production cut. Deliverables under § MVP-0 Scope of `design.md`. Must enforce all eight Day-0 Invariants from day one. |
| `[v1]` | Post-MVP-0 expansion. The 12-step list under "MVP-0 → v1 Sequencing" in `design.md`. v1 closes when every requirement carrying a `[v1]` tag passes its acceptance criteria. |
| `[v1.x]` | After v1 but before v1.1. Smaller increments (e.g. Schwab API, GitHub/Google OAuth in some cases). |
| `[v1.1]` | Live broker adapters runtime-registered. Gated by § Pre-Live-Trading Test Gate + the `LiveEnablementGate` in design.md. |
| `[v1.2]` / `[v1.3]` / `[v1.4]` | Per-roadmap deferrals (OTel, Schwab live, equities corporate actions). |
| `[v2.x]` | Out of scope for the first release; tracked here so the design does not paint itself into a corner. |

A requirement without a phase tag is **`[v1]`** by default. A
requirement may carry multiple phase tags when its acceptance criteria
are split (e.g. Requirement 5 has a CSV-first criterion in `[v1]` and
a Schwab-OAuth criterion in `[v1.x]`).

The authoritative cross-reference for what each phase contains lives
in `design.md` § MVP-0 Scope and Sequencing. Where this requirements
document and `design.md` disagree about phase assignment, **`design.md`
wins** for the affected criterion until a `DECISIONS.md` entry
reconciles them.

### MVP-0 Acceptance (mirrors design.md § MVP-0 Acceptance)

The MVP-0 milestone is closed when **all** are true:

1. All eight Day-0 Invariants are enforced and tested.
2. An operator can run a `BacktestRun` from CLI + dashboard, see its
   artifacts, and re-run it with byte-identical `metrics.json`.
3. An operator can run a `PaperRun` against `PaperBroker`, see fills
   land, and have the risk engine reject orders that violate any
   default check (with the rejection visible in
   `/runs/[runId]/audit`).
4. An operator can compare two runs side-by-side at `/runs/compare`
   and see lever scores update in `/learnings` after each run closes.
5. Hash-chain audit verifier (`python -m monitoring.audit verify
   --tables critical`) is green.
6. `LiveBrokerRegistry.register(BinanceLive())` and
   `register(CoinbaseLive())` raise
   `LiveAdapterRegistrationForbidden`; CI test asserts both.
7. All MVP-0 code paths pass `ruff` + `mypy --strict` +
   `pytest -q -m "not slow and not integration"` +
   `pytest -q -m det` + `pytest -q tests/security/`.

---

## Requirements

> Naming convention: `Requirement N` is functional; non-functional requirements
> live in their own section below. Every acceptance criterion uses EARS
> (`WHEN / IF / WHILE / WHERE / THE SYSTEM SHALL`). Cite criteria from
> `tasks.md` as `_Requirements: N.M_`. Phase tags `[MVP-0]`, `[v1]`,
> `[v1.x]`, `[v1.1]`, `[v2.x]` may appear inline in acceptance criteria;
> default phase is `[v1]`.

---

### Requirement 1: Platform Vision and v1 Acceptance

**User Story:** As a solo quant researcher, I want a self-improving market-intelligence and paper-trading platform, so that I can iteratively discover, validate, and (eventually) deploy strategies without manually wiring data sources or evaluating run outcomes by hand.

#### Acceptance Criteria

1. THE SYSTEM SHALL provide a run-loop based platform that ingests market intelligence, generates predictions, simulates trades, logs decisions with rationale, summarizes outcomes, and recommends improvements for future runs.
2. WHEN the operator starts a 1-hour paper-trading run THE SYSTEM SHALL: ingest market-relevant information from configured sources, generate predictions on the run universe, simulate trades through the risk engine, log every decision with full reasoning context, produce an LLM-generated run summary, and emit a `recommendations.json` artifact for the next run.
3. WHILE any run is executing THE SYSTEM SHALL never place real-money orders unless live mode is explicitly enabled via a multi-step UI confirmation by the operator.
4. THE SYSTEM SHALL keep paper-mode operations fully autonomous and live-mode operations binary-gated, with no implicit "trust ramp".
5. WHEN v1 is considered complete THE SYSTEM SHALL satisfy Acceptance Criterion 1.2 reproducibly with no operator intervention beyond pressing Start and Approve.
6. THE SYSTEM SHALL treat "learn to make money over time" as the singular north-star objective; every subsystem, dashboard view, metric, and alert in this spec MUST trace to that objective in `design.md` § Requirement Traceability.

#### Additional Details

- **Priority:** High **Complexity:** High
- **Dependencies:** Requirements 2, 6, 11, 13, 24, 25.
- **Assumptions:** Solo operator, semi-serious side-project (~2 hr/day), minimal trading background.

---

### Requirement 2: Project Objective and Capital Phases

**User Story:** As the operator, I want a phased path from research to capped live trading, so that the platform can succeed without risking more than $1,000 of real capital in v1.

#### Acceptance Criteria

1. THE SYSTEM SHALL implement a three-phase lifecycle: Research Engine, Paper Trading, Capped Live Trading.
2. THE SYSTEM SHALL start with `live_capital_allocated = $0` and `live_mode_enabled = false`.
3. IF the operator enables live mode THEN THE SYSTEM SHALL enforce a hard live-capital cap of $1,000 USD; raising the cap SHALL require a code-level config change plus a `DECISIONS.md` entry.
4. WHEN 12 months elapse since v1 launch OR live equity reaches $1,200 THE SYSTEM SHALL produce a milestone report comparing actual vs target metrics: `live_equity`, `max_drawdown`, `strategies_live`, `paper_profitability_days`.
5. IF zero strategies survive walk-forward validation and 90 consecutive days of paper trading THEN THE SYSTEM SHALL mark v1 as failed in the dashboard and inhibit live-mode enablement.
6. THE SYSTEM SHALL define v1 success quantitatively as: `strategies_live ≥ 3`, portfolio `Sharpe ≥ 1.2`, `max_drawdown ≤ 15%`, `live_equity ≥ $5,000`.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 14, 15, 24, 25.

---

### Requirement 3: Markets in Scope (Dual-Scope)

**User Story:** As the operator, I want broad market intelligence with narrow gated execution, so that I can monitor everything relevant but only trade where the platform has been proven safe.

#### Acceptance Criteria

1. THE SYSTEM SHALL distinguish two scopes: **monitoring scope** (broad) and **execution scope** (narrow), and SHALL persist them as separate config records editable from the dashboard.
2. THE SYSTEM SHALL accept monitoring data from: crypto spot, crypto perpetuals, US equities, US ETFs, major indexes, FX/commodities (as features), macro event calendars, news/RSS, manual paste-in. THE SYSTEM SHALL allow but defer: X/Twitter automated ingest, YouTube transcripts, Reddit/Discord, on-chain/DeFi, earnings transcripts/SEC filings.
3. WHERE the asset class is crypto spot THE SYSTEM SHALL support execution via Binance and Coinbase adapters.
4. WHERE the asset class is US equities or ETFs THE SYSTEM SHALL support execution via the Alpaca paper-trading adapter only in v1.
5. WHERE the asset class is crypto perpetual futures THE SYSTEM SHALL allow research and paper-trading only and SHALL NOT execute live in v1.
6. THE SYSTEM SHALL configure the v1 core universe to include at minimum: `BTC, ETH, SPY, QQQ, NVDA, AAPL, MSFT, TSLA`; primary timeframe `1h`, secondary `5m`.
7. THE SYSTEM SHALL enforce six hard exclusions, dashboard-tunable but defaulting to: (a) never trade an unsupported asset class; (b) never trade from raw news/social alone; (c) never execute live without human-enabled venue/strategy; (d) never use leverage by default; (e) never bypass the risk engine; (f) never execute on low-confidence entity matching (default `entity_match_threshold ≥ 0.7`).
8. IF an asset class outside the execution scope is referenced by a strategy THEN THE SYSTEM SHALL produce monitoring outputs only and SHALL reject any order for that asset class with `event="exclusion_reject", reason="asset_class_not_in_execution_scope"`.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 4, 5, 24.

---

### Requirement 4: Broker Adapter Scope and Live-Enablement Gate

**User Story:** As the operator, I want every live order to pass through a six-condition enablement gate, so that the platform cannot accidentally trade an unvetted broker, asset, or strategy.

#### Acceptance Criteria

1. `[MVP-0]` `PaperBroker` (canonical deterministic) ships and is the only adapter registered by default. `[v1]` Alpaca (paper) ships. `[v1]` Schwab CSV importer ships. `[v1.x]` Schwab read-only OAuth adapter ships. `[v1.1]` `BinanceLive` and `CoinbaseLive` modules exist as **interface-only stubs** in v1; their classes implement the `Broker` Protocol but `LiveBrokerRegistry.register(...)` raises `LiveAdapterRegistrationForbidden` until the v1.1 pre-live gate clears (see § Pre-Live-Trading Test Gate in design.md). Importing the modules has no side effects. `[v1.1]` Live runtime registration unlocks once `live_adapters_unlocked=true` is written to `config_kv` by an approved RiskAgent decision.
2. `[v1]` THE SYSTEM SHALL persist a per-`(broker, asset_class)` enablement record with `live_enabled: bool`, `paper_enabled: bool`, `last_test_run`, `last_paper_parity_check`. `[MVP-0]` The same table is created day-0 with all rows `live_enabled=false` and `paper_enabled` populated only for `PaperBroker`.
3. `[v1.1]` IF live execution is requested for a venue/asset class THEN THE SYSTEM SHALL require all six conditions: (a) broker adapter implemented (no `NotImplementedError`); (b) paper mode for that adapter exists and passes parity tests; (c) fee/slippage model loaded; (d) risk config for that broker loaded; (e) the originating strategy is in archetype state `R4`; (f) operator has explicitly enabled live execution for that `(venue, asset_class)` via the dashboard. `[v1.1]` A seventh condition `(g) audit_chain_full=true` SHALL gate the unlock once the v1 audit-chain expansion completes.
4. `[v1.1]` WHEN any of the conditions in 4.3 are unmet THE SYSTEM SHALL reject the order, log `event="live_gate_reject"` with the failing condition, and emit a CRITICAL alert.
5. `[MVP-0]` THE SYSTEM SHALL ensure the internal `PaperBroker` is the only broker registered at first install and that all others require explicit configuration.
6. `[MVP-0]` CI test `tests/security/test_live_registration_forbidden.py` SHALL assert that `LiveBrokerRegistry.register(BinanceLive())` and `LiveBrokerRegistry.register(CoinbaseLive())` raise `LiveAdapterRegistrationForbidden` while `live_adapters_unlocked=false`.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 3, 14, 24, 25.

---

### Requirement 5: Schwab Integration (Read-Only v1) — CSV-First, API-Second

**Phase tagging:** This requirement is **CSV-first** in v1 per the
2026-04-25 review (Schwab API integration is `[v1.x]`, after the CSV
path is proven). `design.md` § Component 8 holds the canonical
adapter list.

**User Story:** As the operator, I want my Schwab portfolio visible to the platform and analyzable by the LLM chat, so that I get unified portfolio recommendations without giving the system order-placement authority.

#### Acceptance Criteria

1. `[v1]` THE SYSTEM SHALL provide `SchwabCsvImporter` that parses an operator-uploaded Schwab portfolio export (the standard "Positions" / "Transactions" CSVs Schwab exposes from the brokerage UI) into the read-only `Account` view (`account_balances`, `positions`, `transactions`).
2. `[v1.x]` THE SYSTEM SHALL integrate with Charles Schwab in read-only OAuth mode using `schwab-py` directly OR a community Schwab MCP, choosing whichever is currently maintained at task start.
3. `[v1]` THE SYSTEM SHALL ingest from Schwab at minimum: account balances, current positions, recent transactions. `[v1.x]` Real-time quotes and market-hours metadata.
4. `[v1]` WHERE the LLM chat panel queries Schwab data THE SYSTEM SHALL allow the LLM to read Schwab portfolio context (CSV-imported in v1, OAuth-imported in v1.x) and produce written recommendations.
5. `[MVP-0]` THE SYSTEM SHALL NOT place Schwab orders in any phase. Order-placement code paths for any Schwab adapter SHALL raise an explicit `BrokerOperationDisabled("read_only")` error. CI test asserts.
6. `[v1.x]` WHEN Schwab OAuth tokens expire THE SYSTEM SHALL surface a re-authentication prompt in the UI and SHALL pause Portfolio Review Runs until tokens refresh. `[v1]` In the CSV phase, the dashboard SHALL surface a "Schwab data older than N days" badge when the most recent CSV is older than the configurable freshness threshold.
7. `[v1.x]` THE SYSTEM SHALL store Schwab OAuth credentials only in environment variables or the secret store; THE SYSTEM SHALL NOT log raw tokens. `[v1]` In the CSV phase, the uploaded CSVs SHALL be stored under `/data/schwab_imports/` with a hash and timestamp; raw account numbers SHALL be redacted from logs.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 4, 11.4 (Portfolio Review Run), 21, 41.

---

### Requirement 6: Run as the Atomic Experiment Unit

**User Story:** As the operator, I want every unit of work to be a "run" with a config snapshot, isolated state, and an artifact folder, so that everything the platform does is reproducible and auditable.

#### Acceptance Criteria

1. THE SYSTEM SHALL define a "run" as an asynchronous, configurable market-intelligence experiment with a unique `run_id`, optional `parent_run_id`, `experiment_id`, and per-run `RunConfig`.
2. THE SYSTEM SHALL support run durations of `15m`, `1h` (default), `4h`, `overnight`, `until-stopped`, and `custom`.
3. THE SYSTEM SHALL allow run triggers: manual (UI button), CLI/API, scheduled (cron-style), and AI-initiated for paper/intelligence runs only.
4. THE SYSTEM SHALL NOT permit AI-initiated triggers for live-capital runs.
5. WHEN a run starts THE SYSTEM SHALL freeze its `RunConfig` snapshot, including: duration, mode, objective, universe policy, sources, decision policy, risk profile, learning policy, notification policy.
6. WHILE a run is executing THE SYSTEM SHALL NOT mutate that run's frozen config; AI-proposed changes SHALL apply only to subsequent runs.
7. WHEN a run completes THE SYSTEM SHALL transition status from `running` to one of: `completed | failed | cancelled` and emit an `INFO` `run_ended` notification.

#### Additional Details

- **Priority:** High **Complexity:** High
- **Dependencies:** Requirements 7, 8, 11, 12, 13.

---

### Requirement 7: Concurrent Async Runs and Isolation

**User Story:** As the operator, I want multiple runs to execute concurrently without contaminating each other's state, so that I can run a crypto news scout, an equity earnings scout, and a Schwab portfolio review in parallel.

#### Acceptance Criteria

1. THE SYSTEM SHALL support `≥ 4` concurrent runs without state, PnL, log, or artifact contamination.
2. THE SYSTEM SHALL implement run statuses: `queued | running | paused | completed | failed | cancelled | promoted | archived`.
3. THE SYSTEM SHALL persist per-run snapshots: config, universe, sources, strategy versions, model versions, paper account state, log stream pointer, artifact folder path.
4. WHEN two runs share a strategy THE SYSTEM SHALL ensure each run sees its own paper account state and SHALL NOT cross-write positions or PnL.
5. IF a run process crashes mid-execution THEN THE SYSTEM SHALL transition that run to `failed`, emit a CRITICAL alert, and leave its artifact folder intact for postmortem.

#### Additional Details

- **Priority:** High **Complexity:** High
- **Dependencies:** Requirement 6, Requirement 38.

---

### Requirement 8: Run Memory — Per-Run, Experiment, Global

**User Story:** As the operator, I want explicit memory layers so that learnings compound across runs without poisoning the platform when a single run goes badly.

#### Acceptance Criteria

1. THE SYSTEM SHALL implement three memory layers: **per-run** (events, decisions, trades, logs, positions, PnL, errors), **experiment** (aggregated across same-type runs, e.g. `news_scout_crypto`), **global** (approved learnings only: source scores, feature scores, strategy scores, universe scores, approved config defaults).
2. WHEN a run completes THE SYSTEM SHALL archive per-run memory but SHALL NOT delete it (per Requirement 39 retention).
3. WHEN a run completes THE SYSTEM SHALL update experiment memory with the new run's metrics.
4. IF a learning-update is classified as low-risk per Requirement 17 THEN THE SYSTEM SHALL auto-apply it to global memory; ELSE THE SYSTEM SHALL queue it for operator approval.
5. THE SYSTEM SHALL never let a single failed run mutate global memory without operator approval.
6. WHEN a new run starts THE SYSTEM SHALL inherit global memory (read-only) but SHALL start with fresh per-run accounting.

#### Additional Details

- **Priority:** High **Complexity:** High
- **Dependencies:** Requirements 6, 17.

---

### Requirement 9: Source Confirmation Policy

**User Story:** As the operator, I want a tiered source-confirmation policy, so that the system never trades from a single unconfirmed source.

#### Acceptance Criteria

1. THE SYSTEM SHALL classify every generated insight as one of: `insight_only | paper_trade_candidate | live_trade_candidate`.
2. WHERE a generated insight has only one source THE SYSTEM SHALL classify it as `insight_only` and SHALL NOT generate any trade.
3. WHERE a generated insight has at least two independent sources OR one source plus confirming price/volume behavior THE SYSTEM SHALL allow classification as `paper_trade_candidate`.
4. WHERE a generated insight has multi-source confirmation, validated strategy support (state ≥ R3), risk-engine approval, and explicit live-permission for that venue THE SYSTEM SHALL allow classification as `live_trade_candidate`.
5. THE SYSTEM SHALL log every classification with the contributing sources, confidence score, and the threshold that was met.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 14, 24, 35.

---

### Requirement 10: AI Run Autonomy Boundaries

**User Story:** As the operator, I want explicit AI permission boundaries, so that the system improves itself within safe limits and never escalates its own privileges.

#### Acceptance Criteria

1. THE SYSTEM SHALL allow AI agents to control: run duration recommendation, universe selection, source prioritization, decision timing within a run, paper-trade candidate generation, strategy tweak proposals, next-run config proposals.
2. THE SYSTEM SHALL prohibit AI agents from controlling: live-trading enablement, risk-limit changes, capital-cap changes, broker credentials, kill-switch override.
3. IF an AI agent attempts a forbidden action THEN THE SYSTEM SHALL reject the action, log `event="ai_privilege_denied"` with the requested action and the agent identifier, and emit a WARNING alert.
4. WHILE the AI proposes config changes between runs THE SYSTEM SHALL queue them in an Approval Queue for the operator to review in the dashboard.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 17, 21.

---

### Requirement 11: Run Types Shipping in v1

**User Story:** As the operator, I want four canonical run types covering scout, strategy test, backtest, and portfolio review, so that v1 ships a complete loop.

#### Acceptance Criteria

1. `[MVP-0]` THE SYSTEM SHALL ship three run types: `BacktestRun`, `PaperRun`, `StrategyTestRun`. `[v1]` THE SYSTEM SHALL extend the run-type set with `MarketScoutRun` and `PortfolioReviewRun`. (`PaperRun` was implicit in the prior phrasing under `StrategyTestRun` paper mode; MVP-0 promotes it to a first-class type since the operator's Q11 answer requires a working paper run end-to-end.)
2. `[v1]` WHEN `MarketScoutRun` is started THE SYSTEM SHALL monitor configured sources, predict reactions, simulate trades, and produce next-run recommendations.
3. `[MVP-0]` WHEN `StrategyTestRun` is started THE SYSTEM SHALL execute one specified strategy on live or paper market data with a frozen config snapshot.
4. `[MVP-0]` WHEN `BacktestRun` is started THE SYSTEM SHALL run historical validation per Requirement 26 with deterministic outputs.
5. `[v1]` WHEN `PortfolioReviewRun` is started THE SYSTEM SHALL read Schwab holdings (CSV-imported in v1, OAuth in v1.x), produce a written portfolio review, and emit recommendations classified as `insight_only` per Requirement 9.
6. `[MVP-0]` THE SYSTEM SHALL allow new run types to be added via a typed `RunType` registry without changes to the run engine core.
7. `[MVP-0]` WHEN `PaperRun` is started THE SYSTEM SHALL execute one or more strategies against `PaperBroker` with risk-engine routing, recording fills, equity, and lever-score updates at run-close.

#### Additional Details

- **Priority:** High **Complexity:** High
- **Dependencies:** Requirements 5, 6, 26.

---

### Requirement 12: Run Outputs and Canonical Artifact Folder

**User Story:** As the operator, I want every run to write a canonical artifact folder, so that I can reproduce, audit, and compare runs without spelunking through logs.

#### Acceptance Criteria

1. WHEN a run completes THE SYSTEM SHALL produce an artifact folder at `runs/<YYYY-MM-DD>_<run_id>/` containing at minimum: `config.json`, `events.jsonl`, `decisions.jsonl`, `trades.jsonl`, `metrics.json`, `summary.md`, `recommendations.json`, `run_audit.log`.
2. THE SYSTEM SHALL ensure `summary.md` is generated by an LLM and includes: events observed, predictions made, simulated trades, PnL, missed opportunities, bad calls, source scores, strategy scores, recommended next-run changes.
3. THE SYSTEM SHALL ensure `recommendations.json` is structured and machine-readable so it can be auto-applied or reviewed.
4. IF the LLM fails to produce `summary.md` within `summary_timeout_seconds` THEN THE SYSTEM SHALL produce a deterministic fallback summary from `metrics.json` and `decisions.jsonl` and emit a WARNING alert.
5. THE SYSTEM SHALL register every artifact folder in the MLflow-style experiment store with run metadata.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 6, 8, 22, 41.

---

### Requirement 13: Strategy Archetype Evidence Ladder

**User Story:** As the operator, I want strategy archetypes to occupy dynamic states based on measured evidence, so that the platform learns which edges actually work and demotes ones that stop working.

#### Acceptance Criteria

1. THE SYSTEM SHALL maintain a Strategy Archetype Registry where every archetype has a state in `{X, R0, R1, R2, R3, R4, R5}`.
2. THE SYSTEM SHALL define states as: `X` hard-excluded; `R0` idea/research-only; `R1` implemented in backtest; `R2` walk-forward validated; `R3` paper-trading validated; `R4` live-approved (capped); `R5` scaled live.
3. THE SYSTEM SHALL hard-exclude (state `X`) sub-second / HFT archetypes and active market-making archetypes for v1.
4. WHEN promotion criteria from Requirement 14 are met THE SYSTEM SHALL queue an R-state advancement proposal for operator approval, except auto-eligible transitions per Requirement 17.
5. WHEN demotion triggers per Requirement 14.5 fire THE SYSTEM SHALL automatically demote the archetype by one state and emit a WARNING alert.
6. THE SYSTEM SHALL log every R-state transition with timestamp, run_id reference, evidence summary, and approver identity (operator or `auto`).

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 14, 17.

---

### Requirement 14: Strategy Promotion Gates (Numerical R-Ladder)

**User Story:** As the operator, I want each R-ladder transition gated by concrete numerical thresholds, so that promotions are not subjective.

#### Acceptance Criteria

1. WHERE a strategy is at state `R1` THE SYSTEM SHALL require for `R1 → R2`: walk-forward `Sharpe ≥ 1.0`, max drawdown `≤ 25%`, deflated Sharpe positive, no leakage detected by `research/features/validation.py`, costs included per `configs/costs.yaml`, total trades `≥ 50`.
2. WHERE a strategy is at state `R2` THE SYSTEM SHALL require for `R2 → R3`: `≥ 30 days` paper trading, live Sharpe within `±25%` of backtest Sharpe, zero CRITICAL alerts during the window.
3. WHERE a strategy is at state `R3` THE SYSTEM SHALL require for `R3 → R4`: `≥ 90 days` paper trading with cumulative PnL > 0, max drawdown `≤ 15%`, **explicit operator approval through the dashboard**.
4. WHERE a strategy is at state `R4` THE SYSTEM SHALL require for `R4 → R5`: `≥ 30 days` live trading with cumulative PnL > 0, zero critical operational failures, **explicit operator approval through the dashboard**.
5. THE SYSTEM SHALL auto-trigger demotion (any R → R-1) when any of: live drawdown exceeds limit, live Sharpe collapses below 0.5, observed slippage exceeds `2× expected`, model drift detected, data-quality failure recorded.
6. THE SYSTEM SHALL persist all promotion-gate thresholds in dashboard-editable config; defaults are listed in 14.1–14.5.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 13, 24, 26.

---

### Requirement 15: Adaptive Universe Tiers and Bandit Allocation

**User Story:** As the operator, I want the universe to adapt based on prior usefulness, so that attention concentrates on assets the platform has shown it can read.

#### Acceptance Criteria

1. THE SYSTEM SHALL maintain four universe tiers: `Core` (always monitored), `Candidate` (monitored when active), `Discovery` (sampled occasionally), `Excluded` (blocked).
2. THE SYSTEM SHALL set the v1 default `Core` to `{BTC, ETH, SPY, QQQ, NVDA, AAPL, MSFT, TSLA}`, dashboard-editable.
3. WHILE selecting the universe for a new run THE SYSTEM SHALL apply an exploration/exploitation policy with default split 80% proven (`Core ∪ high-score Candidate`) / 20% discovery (bandit-allocated from `Candidate ∪ Discovery`).
4. THE SYSTEM SHALL log per-run: included symbols with reasons, excluded high-interest symbols with reasons.
5. WHEN a symbol's score falls below `excluded_threshold` for `≥ 5` runs THE SYSTEM SHALL move the symbol to `Excluded` and emit an INFO alert.
6. THE SYSTEM SHALL never allow a Core symbol to be auto-excluded; demotion requires operator approval.

#### Additional Details

- **Priority:** Medium **Complexity:** Medium
- **Dependencies:** Requirements 6, 8.

---

### Requirement 16: LLM Calibration as a Signal Source

**User Story:** As the operator, I want the LLM treated as just another signal source whose calibration is scored over time, so that hallucinated confidence does not silently drive bad runs.

#### Acceptance Criteria

1. `[MVP-0]` THE SYSTEM SHALL record per-LLM-call: prompt name + version (per `research/llm/prompts.py`), provider, model, temperature, seed, response, declared confidence (if any), token counts, **and a required `task_type` enum value**. Calls without `task_type` SHALL be rejected at the `research.llm.client.chat()` boundary.
2. `[MVP-0]` THE SYSTEM SHALL define an initial `task_type` enum: `sentiment_extraction`, `run_summary`, `asset_identification`, `trade_thesis`, `feature_naming`, `chat_response`. Adding a new value requires a `DECISIONS.md` entry plus a row in `llm_calibration_outcome_mapping.yaml`.
3. `[v1]` WHEN a run that relied on LLM-derived inputs completes THE SYSTEM SHALL evaluate calibration **per `task_type`** by mapping declared confidence to the task's realized-outcome metric (Brier for `sentiment_extraction`, accuracy for `run_summary` against operator vote, exact-match for `asset_identification`, IC for `trade_thesis`) and update `llm_calibration` keyed by `(task_type, model, prompt_hash)`.
4. `[v1]` IF LLM calibration for a given `task_type` drops below `min_calibration_threshold[task_type]` (configurable; default 0.5) over a rolling window THEN THE SYSTEM SHALL demote outputs of that task type to `insight_only` and emit a WARNING alert. Other task types SHALL be unaffected.
5. `[MVP-0]` THE SYSTEM SHALL never let LLM judgment alone trigger a paper or live trade — the deterministic strategy + risk path is required (per Requirement 23).
6. `[v1]` The dashboard `/configuration/llm` route SHALL surface a calibration card **per `task_type`** with rolling metric, sample count, freshness chip, and a per-model breakdown. There SHALL be no global "LLM calibration score".

#### Additional Details

- **Priority:** Medium **Complexity:** Medium
- **Dependencies:** Requirements 9, 22, 23, 41.

---

### Requirement 17: Auto-Apply vs Approval-Required Changes

**User Story:** As the operator, I want low-risk improvements applied automatically and high-risk changes queued for approval, so that the platform can self-improve without paging me for trivia.

#### Acceptance Criteria

1. THE SYSTEM SHALL classify proposed changes into two buckets: **auto-apply** (source priority, watchlist ranking, summary templates, paper-only strategy parameters within bounds) and **approval-required** (risk limits, live-trading enablement, capital allocation, broker permissions, R-state promotions to `R3` and beyond).
2. WHEN an auto-apply change is generated THE SYSTEM SHALL apply it to the next run's config, log `event="auto_apply"` with the diff, and surface it in the dashboard activity feed.
3. WHEN an approval-required change is generated THE SYSTEM SHALL queue it in the Approval Queue with full context (run that produced it, expected impact, evidence) and emit an INFO alert.
4. THE SYSTEM SHALL never apply an approval-required change without an operator action recorded with timestamp and approver identity.
5. IF an auto-apply change exceeds defined bounds (e.g. proposing a parameter outside its allowed range) THEN THE SYSTEM SHALL reroute it to approval-required and log `event="auto_apply_promoted_to_approval"`.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 8, 10, 14.

---

### Requirement 18: Manual Insight Intake (LLM Paste-In Terminal) `[v1]`

**Phase:** Not in MVP-0. Lands in step 2 of the MVP-0 → v1 sequencing
in `design.md` § MVP-0 Scope.

**User Story:** As the operator, I want to paste creator commentary, news links, threads, or transcripts into a terminal and get a structured market interpretation, so that I can capture context that automated ingestion misses.

#### Acceptance Criteria

1. THE SYSTEM SHALL provide an Insight Intake surface in the dashboard accepting text and URLs.
2. WHEN the operator submits text or a URL THE SYSTEM SHALL produce a structured response with fields: `assets`, `catalyst`, `sentiment`, `confidence`, `time_horizon`, `recommendation`, `trade_allowed`, `reason`, `supporting_evidence`, `risk_factors`.
3. THE SYSTEM SHALL set `trade_allowed = false` on every Insight Intake response in v1.
4. THE SYSTEM SHALL classify Insight Intake outputs as `insight_only` or, if combined with a confirming source/strategy, allow upgrade to `paper_trade_candidate` per Requirement 9.
5. WHEN entity matching confidence falls below `entity_match_threshold` (default 0.7) THE SYSTEM SHALL flag the response and require operator review before any downstream use.
6. THE SYSTEM SHALL persist every intake submission and response under `data/insights/<date>/<insight_id>.json`.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 9, 21, 22.

---

### Requirement 19: Market Intelligence Ingestion Sources and Latency

**User Story:** As the operator, I want every monitored source to have a defined latency contract, so that the system knows what is fresh and what is stale.

#### Acceptance Criteria

1. THE SYSTEM SHALL ingest the following MUST-v1 sources with their latency targets: price OHLCV crypto+equities (WebSocket realtime + 1-min aggregation fallback); news/RSS + macro calendar (poll every `≤ 10 min`); manual paste-in (on-demand).
2. THE SYSTEM SHALL architecturally allow but defer to v2: X/Twitter (no acceptable free tier); YouTube transcripts (`yt-dlp` + `whisper.cpp`, poll-30m); Reddit/Discord (poll-30m); on-chain/DeFi (poll-15m); funding rates (poll-5m); earnings transcripts/SEC filings (poll-60m).
3. THE SYSTEM SHALL compute and persist per-feature engineered signals in three categories supported from day one: derivatives positioning (funding-rate z-score, OI change, liquidation clusters), regime detection (realized volatility, vol clustering, trend strength, liquidity proxy), cross-asset flow (relative strength, ETF flows, correlation breakdowns).
4. WHEN any MUST-v1 source's last successful fetch exceeds `staleness_threshold` THE SYSTEM SHALL emit the data-feed-stale alert per Requirement 31 and SHALL mark dependent decisions as `degraded`.
5. THE SYSTEM SHALL allow operator to disable any source from the dashboard, in which case the source SHALL NOT contribute to any run's confirmation count.

#### Additional Details

- **Priority:** High **Complexity:** High
- **Dependencies:** Requirements 9, 18, 31, 38.

---

### Requirement 20: Pipeline Integrity (Signal → Strategy → Risk → Execution)

**User Story:** As the operator, I want one and only one path from a signal to a placed order, so that no LLM, intake, or convenience shortcut can reach the broker.

#### Acceptance Criteria

1. THE SYSTEM SHALL implement the order pipeline as: signal → strategy → `risk.engine.RiskEngine.check_and_size` → broker. No other path SHALL exist.
2. THE SYSTEM SHALL ensure signals cannot place trades; only strategies can produce target positions, and only risk-approved orders can reach a broker.
3. WHERE the call path is `execution/*` THE SYSTEM SHALL NOT import any module under `research.llm` (per `.cursor/rules/llm-usage.mdc`).
4. THE SYSTEM SHALL enforce 20.3 with `tests/security/test_llm_isolation.py` running in CI on every PR.
5. THE SYSTEM SHALL NOT accept any flag named or aliased to `skip_risk`, `bypass_risk`, `RISK_BYPASS`, `DISABLE_RISK`, or `--no-risk`. CI SHALL grep for these and fail builds that introduce them (per `.cursor/rules/risk-management.mdc`).

#### Additional Details

- **Priority:** High **Complexity:** Low (already partially enforced)
- **Dependencies:** Requirements 22, 23, 24.

---

### Requirement 21: Dashboard LLM Chat Panel

**Phase:** `[v1]`. The chat panel is **not in MVP-0**; lands in step 5
of the MVP-0 → v1 sequencing. MVP-0 surfaces a read-only
`LLMSummaryCard` on `/runs/[runId]` rendered from the run-close
summary, with no command bus.

**User Story:** As the operator, I want a chat panel in the dashboard that talks to the platform via API/MCP tools, so that I can ask questions, propose changes, and approve actions without leaving the UI.

#### Acceptance Criteria

1. `[v1]` THE SYSTEM SHALL expose a chat panel in the Next.js dashboard as the **only v1 LLM conversation surface**.
2. THE SYSTEM SHALL ensure the chat panel interacts with platform state only through the platform API/MCP tool layer; it SHALL NOT reach around through direct DB/file access.
3. THE SYSTEM SHALL grant the chat panel the following capabilities: read-only Q&A on runs/results/Schwab; propose strategy/universe/config changes; apply approved changes to next-run config; start/stop/pause runs; place paper trades within an active paper run when allowed by run policy.
4. THE SYSTEM SHALL prohibit the chat panel from placing live trades directly. Live trades SHALL require: live-mode enablement, deterministic risk-engine approval, capital cap, supported broker adapter, trade-ticket confirmation, audit logging.
5. WHEN the chat panel performs any action THE SYSTEM SHALL log it with `event="chat_action"` including the user prompt hash, action type, parameters, and outcome.
6. THE SYSTEM SHALL keep Cursor IDE chat, CLI, Discord bot, and voice surfaces **out of v1** but architecturally compatible for v2.

#### Additional Details

- **Priority:** High **Complexity:** High
- **Dependencies:** Requirements 10, 22, 41.

---

### Requirement 22: Multi-Provider LLM Layer

**User Story:** As the operator, I want pluggable LLM providers so I can use local Ollama by default, paid APIs when I want speed, and switch per task.

#### Acceptance Criteria

1. `[MVP-0]` THE SYSTEM SHALL implement a provider layer in `research/llm/` behind an `LLMProvider` Protocol with `OllamaProvider` as the only registered adapter. `[v1]` THE SYSTEM SHALL add a `LiteLLMProvider` adapter supporting `openai` and `anthropic` providers behind the same Protocol.
2. `[v1]` THE SYSTEM SHALL select the LLM provider per task type via dashboard-editable config (e.g. cheap+local for entity extraction, large+slow for run retrospective). `[MVP-0]` Per-task-type provider selection is a YAML knob; defaults to Ollama for every task type.
3. `[v1]` WHEN an `openai` or `anthropic` API key is absent or rate-limited THE SYSTEM SHALL fall back to `ollama` and log `event="llm_fallback"`.
4. `[MVP-0]` THE SYSTEM SHALL load all LLM API keys from environment variables only and SHALL NOT log raw key material.
5. `[MVP-0]` THE SYSTEM SHALL accommodate models up to `qwen2.5:32b` Q4 on a 24GB GPU; if a configured Ollama model does not fit THE SYSTEM SHALL emit a CRITICAL alert and refuse to start the run.
6. `[MVP-0]` THE SYSTEM SHALL never require a paid API to operate. v1 functionality SHALL be achievable on Ollama alone.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 16, 21, 41.

---

### Requirement 23: LLM Isolation From Trading Path

**User Story:** As the operator, I want an enforced firewall between LLM-derived outputs and order execution, so that hallucinated trade ideas can never reach the broker.

#### Acceptance Criteria

1. THE SYSTEM SHALL prohibit any module under `execution/` from importing any module under `research.llm`, transitively or directly.
2. THE SYSTEM SHALL enforce 23.1 in CI via `tests/security/test_llm_isolation.py` (already in scaffold).
3. THE SYSTEM SHALL allow the LLM to produce: alerts, watchlist items, research notes, candidate signals, paper-trade candidates — and nothing else that touches the order path.
4. THE SYSTEM SHALL require that any LLM-derived input that influences a strategy decision pass through the deterministic feature pipeline (`research/features/`) and be persisted as a numeric feature with a feature card before use.

#### Additional Details

- **Priority:** High **Complexity:** Low (architecture already enforces this)
- **Dependencies:** Requirements 20, 22.

---

### Requirement 24: Risk Limits and Kill Switch

**User Story:** As the operator, I want hard, dashboard-tunable risk limits and a kill switch, so that no single bug or strategy run can blow up the account.

#### Acceptance Criteria

1. THE SYSTEM SHALL enforce risk limits with these defaults, dashboard-tunable: `max_risk_per_trade = 1%`, `max_daily_loss = 3%`, `kill_switch_drawdown = 20%`, `max_gross_exposure = 1.0×`, `max_leverage = 1.0×`, `max_per_symbol_weight = 25%`, `live_capital_cap = $1,000`, `min_order_notional = $10`.
2. THE SYSTEM SHALL route every order — backtest, paper, or live — through `risk.engine.RiskEngine.check_and_size` with no bypass possible.
3. WHEN any risk limit is breached THE SYSTEM SHALL reject the order, log `event="risk_reject"` with the rule name, and emit a WARNING alert; if the breach implicates the kill switch THEN it SHALL emit a CRITICAL alert and trigger the kill switch.
4. WHEN the kill switch fires THE SYSTEM SHALL: cancel all open orders across all brokers, halt all running live-mode runs, set `live_mode_enabled = false`, and require operator action to resume.
5. THE SYSTEM SHALL NOT auto-clear the kill switch. Resumption SHALL require operator confirmation through a multi-step UI action.
6. WHERE risk-limit changes are proposed THE SYSTEM SHALL classify them as approval-required per Requirement 17 and log every change to `DECISIONS.md` if a default limit shifts.

#### Additional Details

- **Priority:** High **Complexity:** Medium (engine exists in scaffold, needs UI tuning + kill-switch wiring)
- **Dependencies:** Requirements 17, 20, 31.

---

### Requirement 25: Trust Model — Paper Autonomous, Live Binary

**User Story:** As the operator, I want paper mode fully autonomous and live mode binary-gated, so that the platform can iterate freely without me, and only deliberate human action moves real money.

#### Acceptance Criteria

1. WHILE in paper mode THE SYSTEM SHALL allow the platform to start runs, make predictions, simulate trades, and auto-apply low-risk changes per Requirement 17 without supervision.
2. THE SYSTEM SHALL keep `live_mode_enabled` defaulting to `false` and SHALL NOT auto-flip it under any condition.
3. WHEN the operator enables live mode through the dashboard THE SYSTEM SHALL require a multi-step confirmation that includes typing the dollar cap and acknowledging the active venue/asset class.
4. THE SYSTEM SHALL never recommend live-mode enablement in any LLM-generated output. The dashboard SHALL surface readiness indicators, but the action SHALL remain operator-initiated.
5. THE SYSTEM SHALL display live-mode status prominently in the dashboard header at all times.

#### Additional Details

- **Priority:** High **Complexity:** Low
- **Dependencies:** Requirements 4, 24, 21.

---

### Requirement 26: Backtest Reproducibility and Determinism

**Phase:** `[MVP-0]` for all criteria except 26.6 (long-horizon
single-stock equities guard) which is also `[MVP-0]` because it
prevents silent corruption.

**User Story:** As the operator, I want every backtest to be byte-identical when re-run with the same inputs, so that I can trust the metrics.

#### Acceptance Criteria

1. `[MVP-0]` WHEN given the same `(strategy_version, dataset_version, feature_set_version, parameters, git_commit, seeds, python_version, pinned_deps_hash)` THE SYSTEM SHALL produce byte-identical `metrics.json` output. Determinism CI runs on every PR.
2. `[MVP-0]` THE SYSTEM SHALL write a `manifest.json` for every backtest run containing: `strategy_id`, `strategy_version`, `dataset_id`, `dataset_version`, `feature_set_version`, `params_hash`, `config_hash`, `git_commit`, `seed`, `cost_model_version`, `timestamp_utc`, `python_version`, `pinned_deps_hash`.
3. `[MVP-0]` Every JSON artifact under `backtests/results/` SHALL be written through `backtests.io.canonical_json.dumps`. The serializer SHALL enforce: sorted keys recursively; floats serialized as `Decimal`-derived strings with fixed precision per `metrics_schema.yaml`; ISO 8601 UTC timestamps with explicit `Z` suffix and 6-digit microseconds; NaN and Inf forbidden (raises `NonFiniteValueError`); sets forbidden in artifacts; UTF-8 LF with trailing newline; compact separators (`","` and `":"`); top-level `schema_version: "1"`. CI test asserts every `*.json` round-trips through the canonical serializer with zero diff.
4. `[MVP-0]` THE SYSTEM SHALL include realistic frictions in every backtest: fees, slippage, latency assumptions, liquidity constraints (per `configs/costs.yaml`).
5. `[v1]` THE SYSTEM SHALL provide walk-forward and purged-k-fold cross-validation with embargo (already in `research/cv.py`) and SHALL refuse to promote a strategy past `R1 → R2` without a walk-forward run.
6. `[MVP-0]` WHEN a backtest completes THE SYSTEM SHALL `INSERT` a row into the `backtests` DuckDB table so the backend API and frontend immediately reflect it.
7. `[MVP-0]` WHEN a `BacktestSpec` satisfies `(asset_class == "us_equity") AND (len(universe) == 1) AND (window_days > 5 × 365)` (or the strategy concentrates > 80% time in a single equity) THE SYSTEM SHALL set `manifest.json.degraded = true`, annotate `metrics.json.corp_actions_warning = "uncovered"`, surface a yellow chip on the run detail page, and cap the resulting R-state at `R-1` until v1.4 corporate-action handling lands.

#### Additional Details

- **Priority:** High **Complexity:** Medium (engine exists in scaffold; manifest writer exists; needs DB insert wiring)
- **Dependencies:** Requirements 14, 27, 28.

---

### Requirement 27: Strategy Versioning

**User Story:** As the operator, I want strategies to be immutable once shipped and to carry an explicit version, so that I can reproduce or roll back without ambiguity.

#### Acceptance Criteria

1. THE SYSTEM SHALL require every strategy to declare: `strategy_id`, `version` (`v<N>`), `author`, `creation_date`, `notes`.
2. THE SYSTEM SHALL never mutate a published strategy in place. Changes SHALL produce a new version (e.g. `momentum_v1` → `momentum_v2`).
3. WHEN a backtest, paper run, or live run references a strategy THE SYSTEM SHALL resolve it by `(strategy_id, version)` and persist that pair in the run's frozen config.
4. THE SYSTEM SHALL surface strategy versions in the dashboard with a diff view between adjacent versions.

#### Additional Details

- **Priority:** Medium **Complexity:** Low
- **Dependencies:** Requirements 6, 13, 26.

---

### Requirement 28: Dataset Versioning and Snapshots

**User Story:** As the operator, I want every dataset used by a backtest to be versioned, so that "the data changed" is never an unanswered question.

#### Acceptance Criteria

1. THE SYSTEM SHALL store dataset snapshots in Parquet under `datasets/<source>_<symbol>_<timeframe>_<from>_<to>.parquet` with a content-hash filename suffix.
2. THE SYSTEM SHALL persist a `dataset_id` and `version` for every snapshot in DuckDB.
3. WHEN a backtest is requested THE SYSTEM SHALL refuse to run if the referenced `dataset_id` is missing and SHALL log `event="dataset_missing"`.
4. THE SYSTEM SHALL never overwrite a published dataset snapshot. Re-ingestion SHALL produce a new versioned snapshot.

#### Additional Details

- **Priority:** Medium **Complexity:** Medium
- **Dependencies:** Requirements 26, 32.

---

### Requirement 29: Feature Registry

**User Story:** As the operator, I want every feature registered with declared inputs, lookback, and output, so that no agent can introduce a hidden look-ahead.

#### Acceptance Criteria

1. THE SYSTEM SHALL maintain a Feature Registry in `research/features/` where every feature declares: `name`, `inputs`, `lookback_window`, `output_column`, `version`, `author`, `look-ahead caveats`.
2. THE SYSTEM SHALL run `research.features.validation.assert_no_lookahead` against every registered feature in CI.
3. THE SYSTEM SHALL surface feature usefulness scores per archetype/run in the dashboard so the operator can see which features earn their place.
4. WHEN a strategy references a feature THE SYSTEM SHALL resolve it by `(feature_name, version)` and persist that pair in the strategy's frozen config.

#### Additional Details

- **Priority:** Medium **Complexity:** Low (validators exist in scaffold; needs registry surface + UI)
- **Dependencies:** Requirements 26, 27, 28.

---

### Requirement 30: Data Freshness and Stale-Data Handling

**User Story:** As the operator, I want stale data to invalidate signals, so that the system doesn't trade off prices that are minutes old.

#### Acceptance Criteria

1. THE SYSTEM SHALL maintain a `last_received_at` timestamp per `(source, symbol)` and compute `staleness = now − last_received_at`.
2. WHERE `staleness > staleness_threshold` (default `5 min` for price; per-source defaults configurable) THE SYSTEM SHALL mark dependent decisions as `degraded` and SHALL NOT generate `live_trade_candidate` classifications using that source.
3. WHEN data is stale for `> 5 min` THE SYSTEM SHALL emit a CRITICAL `data_feed_stale` alert per Requirement 31.
4. WHEN data freshness is restored THE SYSTEM SHALL emit an INFO `data_feed_recovered` alert and resume normal operation.

#### Additional Details

- **Priority:** High **Complexity:** Low
- **Dependencies:** Requirements 19, 31, 38.

---

### Requirement 31: Notification System and Severity Routing

**User Story:** As the operator, I want a notification system with three severity levels and explicit channel routing, so that critical events page me but informational events don't drown me.

#### Acceptance Criteria

1. THE SYSTEM SHALL implement three severities: `INFO`, `WARNING`, `CRITICAL`.
2. THE SYSTEM SHALL implement v1 channels: in-app UI notification center, Discord webhook, Email (SMTP). SMS/push and Slack/Telegram are deferred.
3. THE SYSTEM SHALL route by default: `INFO` → UI (optional Discord); `WARNING` → UI + Discord; `CRITICAL` → UI + Discord + Email.
4. THE SYSTEM SHALL emit notifications using a structured schema: `{event_type, severity, message, strategy, run_id, timestamp_utc, channels, payload}`.
5. THE SYSTEM SHALL persist every notification in the `notifications` DuckDB table with retention per Requirement 39.
6. WHEN a channel send fails THE SYSTEM SHALL retry with exponential backoff up to 3 attempts, then fall back to UI-only and log `event="notif_channel_degraded"`.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirement 32.

---

### Requirement 32: The Seven Must-Have Operational Alerts

**User Story:** As the operator, I want seven canonical operational alerts wired and tested, so that the system can never silently fail.

#### Acceptance Criteria

1. THE SYSTEM SHALL implement and route the following alerts with stated severities: (1) Risk breach → CRITICAL; (2) Kill switch triggered → CRITICAL; (3) Exchange/broker API failure → CRITICAL; (4) Data feed stale/disconnected → CRITICAL; (5) Execution slippage anomaly → WARNING; (6) Runaway trade loop (orders-per-minute spike or duplicates) → CRITICAL; (7) Strategy performance degradation vs backtest distribution → WARNING.
2. THE SYSTEM SHALL include test fixtures that synthetically trigger each of the seven alerts and verify route + payload, run in CI.
3. WHEN alert (3), (4), or (6) fires THE SYSTEM SHALL automatically pause affected runs.
4. WHEN alert (1) or (2) fires THE SYSTEM SHALL trigger the kill switch per Requirement 24.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 24, 30, 31.

---

### Requirement 33: UI as Source of Truth for Configuration — Phased

**Phase tagging:** MVP-0 ships **read-only** dashboard config views.
The full UI write-path becomes mandatory in v1 per the operator's Q4
answer ("Yes, all knobs in UI before engine"); the binding sequencing
is "engine becomes autonomous (paper-runs trigger themselves and
auto-apply low-risk levers) only after v1 step 6 lands". Until v1
step 6, configuration is YAML-seeded into DuckDB and edited by PR +
reseed.

**User Story:** As the operator with minimal trading background, I want every config knob editable from the dashboard, so that I never edit YAML or Python to operate the platform.

#### Acceptance Criteria

1. `[v1]` THE SYSTEM SHALL expose every runtime configuration knob in the dashboard with a corresponding UI control: risk limits, run config, universe, sources, strategies, notifications, LLM provider, broker keys, kill-switch state, promotion gates. `[MVP-0]` `/configuration/*` SHALL render the same set of knobs as **read-only views** sourced from DuckDB so the dashboard UX contract is locked from day 0.
2. `[MVP-0]` THE SYSTEM SHALL persist the active configuration in DuckDB (`config_kv` and `config_history`) and treat YAML files in `configs/` as the **boot-time seed** in MVP-0 / **import-export format** in v1. The "configs over code" principle holds in both phases. `[MVP-0]` On boot, the YAML seeds are imported into `config_kv` if and only if `config_kv` is empty (idempotent seed).
3. `[v1]` WHEN the operator changes a config value in the UI THE SYSTEM SHALL persist it, write a `config_history` row (hash-chained from MVP-0 — see Requirement 36 / design.md § Compliance), apply it to subsequent runs (never a frozen running run), and emit a `config_change` event.
4. `[v1]` THE SYSTEM SHALL provide config import/export from the dashboard so the operator can snapshot a config to YAML and restore it later.
5. `[v1]` WHERE a config change is approval-required per Requirement 17 THE SYSTEM SHALL require multi-step confirmation in the UI before persisting.
6. `[MVP-0]` Operator-controlled MVP-0 actions (kill-switch toggle, run start/stop) SHALL still write to `config_history` even though the broader UI write surface is `[v1]`. This avoids backfilling audit later.

#### Additional Details

- **Priority:** High **Complexity:** High
- **Dependencies:** Requirements 8, 17, 24.

---

### Requirement 34: Beginner-Safe UX

**User Story:** As an operator with minimal trading background, I want the UI to teach me as I go, so that I can configure the platform safely without quant expertise.

#### Acceptance Criteria

1. THE SYSTEM SHALL show explanatory tooltips on every quant term in the UI, including at minimum: Sharpe, drawdown, slippage, look-ahead, walk-forward, deflated Sharpe, hit rate, turnover, max gross exposure, leverage.
2. THE SYSTEM SHALL provide a Glossary page accessible from the main navigation.
3. THE SYSTEM SHALL pre-fill every form with safe defaults (per Requirement 24 risk limits, etc.).
4. WHERE an action carries irreversible or high-blast-radius consequence (live mode, kill switch override, raising capital cap) THE SYSTEM SHALL require multi-step confirmation including typing a confirmation phrase.
5. THE SYSTEM SHALL display the current capital cap and live-mode state prominently in the dashboard header on every page.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 21, 33.

---

### Requirement 35: Frontend Realtime Update Strategy

**User Story:** As the operator, I want live updates on the run page and refresh-on-load elsewhere, so that I can watch a run unfold without paying for realtime everywhere.

#### Acceptance Criteria

1. WHILE a run is executing THE SYSTEM SHALL push events to the run page via WebSocket or Server-Sent Events at endpoint `/ws/runs/{run_id}` or equivalent.
2. THE SYSTEM SHALL deliver decision events and trade events to the run page within `≤ 500 ms` p95 of internal emission.
3. WHERE a page is non-run (overview, strategies, signals, backtests, health, diagnostics) THE SYSTEM SHALL refresh on load with an optional 30-second background poll.
4. WHEN the WebSocket disconnects THE SYSTEM SHALL auto-reconnect with exponential backoff and SHALL resume from the last seen `event_id` to avoid gaps.

#### Additional Details

- **Priority:** Medium **Complexity:** Medium
- **Dependencies:** Requirements 12, 21.

---

### Requirement 36: Per-Decision Explainability and Trade Audit

**User Story:** As the operator, I want every simulated trade to expose its full evidence chain, so that I can verify the system's reasoning and learn from it.

#### Acceptance Criteria

1. THE SYSTEM SHALL display a one-line summary per simulated trade: `(symbol, side, size, price, why)`.
2. THE SYSTEM SHALL provide click-through drill-down to the full evidence chain: triggering sources with confidence, features at decision time, model output and confidence, LLM reasoning (if any), risk-engine pass/reject record, run-config snapshot link.
3. THE SYSTEM SHALL persist every trade decision in `decisions.jsonl` and `trades.jsonl` per Requirement 12 with full audit context.
4. THE SYSTEM SHALL surface a "Model Judgment" panel per trade showing: strategy + version, signal score, every applied filter pass/fail, risk check result, model + version.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 12, 26, 27.

---

### Requirement 37: Hosting Topology, GPU, and Network Resilience

**User Story:** As the operator, I want the platform to deploy as a Docker stack on my Unraid box and survive transient network failures, so that runs scheduled overnight don't silently die.

#### Acceptance Criteria

1. THE SYSTEM SHALL deploy as a Docker Compose stack on the Unraid host, joined to the existing `trading-net` external network alongside pre-existing `ollama` and `hermes` containers.
2. THE SYSTEM SHALL ship containers: `frontend`, `backend`, `trading-engine`, `redis`, `duckdb` (volume-owner), `mlflow` (experiment store), inheriting the topology in `docker-compose.yml`.
3. THE SYSTEM SHALL accommodate the operator's RTX 3090 / 24GB VRAM via the existing Ollama container; the LLM provider config SHALL select per-task model sizes that fit.
4. WHEN any external boundary (exchange WS, REST API, Schwab, news feed, LLM API, MCP) disconnects THE SYSTEM SHALL retry with exponential backoff (per existing `tenacity` usage), apply circuit-breaker semantics, and log every reconnect.
5. WHEN the container host restarts THE SYSTEM SHALL recover state for any in-flight run by either resuming from the last persisted checkpoint or transitioning the run to `failed` with a logged reason. THE SYSTEM SHALL NOT silently drop runs.
6. THE SYSTEM SHALL run all containers as non-root users (per existing Dockerfiles).

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirement 31.

---

### Requirement 38: Data Retention and Backup

**User Story:** As the operator, I want infinite run history but a size guardrail, so that disk use is monitored without losing audit trail.

#### Acceptance Criteria

1. THE SYSTEM SHALL retain run history indefinitely by default; deletion or archival SHALL be explicit operator action.
2. WHILE total `data/` size exceeds 800 GB THE SYSTEM SHALL emit a WARNING `storage_pressure` alert; WHEN it exceeds 1 TB THE SYSTEM SHALL emit a CRITICAL alert.
3. THE SYSTEM SHALL allow the operator to archive or delete runs from the dashboard, with archive producing a zstd-compressed tarball moved to a configurable cold-storage path.
4. THE SYSTEM SHALL rely on Unraid appdata backup for the canonical backup path; no separate cloud target is required in v1.
5. THE SYSTEM SHALL ensure that recoverable data (market data, news archives) can be re-ingested from sources after data loss without operator intervention beyond starting a re-ingest job.
6. THE SYSTEM SHALL ingest at first install with these depths, dashboard-tunable: crypto OHLCV `1m=90d`, `1h=5y`, `1d=10y`; equity OHLCV `1m=30d`, `1h=5y`, `1d=20y`; news/RSS rolling 30d; run logs infinite.

#### Additional Details

- **Priority:** Medium **Complexity:** Low
- **Dependencies:** Requirements 6, 28.

---

### Requirement 39: Free-Only Tooling Constraint

**User Story:** As the operator, I want zero recurring SaaS costs, so that monthly platform cost is bounded by hardware.

#### Acceptance Criteria

1. THE SYSTEM SHALL NOT depend on any paid SaaS subscription for v1 functionality. Paid LLM APIs are supported as **optional**, never required.
2. THE SYSTEM SHALL prefer free / self-hosted tools per category: news/RSS via free Finnhub tier + RSS aggregator; YouTube via `yt-dlp` + `whisper.cpp`; LLM via Ollama default with optional OpenAI/Anthropic keys; market data via CCXT (crypto) and Alpaca free tier + `yfinance` (equities); experiment tracking via self-hosted MLflow; notifications via Discord webhook + `smtplib`; background jobs via APScheduler in v1; vector store via Qdrant or Chroma local; storage via local disk + DuckDB; auth via NextAuth self-hosted.
3. WHEN a paid feature is enabled by the operator (e.g. OpenAI API key) THE SYSTEM SHALL surface estimated monthly cost in the UI based on observed token usage.

#### Additional Details

- **Priority:** Medium **Complexity:** Medium
- **Dependencies:** Requirement 22.

---

### Requirement 40: CI/CD and Deployment Process

**User Story:** As the operator, I want CI to enforce quality without auto-deploying to my Unraid box, so that I retain manual control over what lands in prod.

#### Acceptance Criteria

1. THE SYSTEM SHALL run CI on hosted GitHub Actions runners on every push and PR to `main`. Self-hosted Unraid runners are deferred.
2. THE SYSTEM SHALL run in CI: `ruff check .`, `ruff format --check`, `mypy --strict`, `pytest -q` (unit + strategy + security), `pytest -q -m e2e`, backtest smoke, AI evals (deepeval offline + promptfoo offline), Docker image builds (no push), `gitleaks` secret scan.
3. THE SYSTEM SHALL build but NOT push Docker images in v1. Image registry deferred.
4. THE SYSTEM SHALL deploy by manual operator action: `git pull && docker compose pull && docker compose up -d` on the Unraid box.
5. THE SYSTEM SHALL provide a documented rollback procedure: `git checkout <prev_commit> && docker compose up -d`.

#### Additional Details

- **Priority:** Medium **Complexity:** Low (existing `ci.yml` already covers most of this)
- **Dependencies:** Requirement 37.

---

### Requirement 41: Observability and Structured Logging

**User Story:** As the operator, I want structured logs and metrics for every meaningful event, so that I can debug without cracking open Python.

#### Acceptance Criteria

1. `[MVP-0]` THE SYSTEM SHALL emit structured logs (JSON when `ENV != dev`) via `monitoring/logger.py` for every: signal generation, model prediction, trade decision, order placement, risk decision, alert, config change, run lifecycle event, LLM call.
2. `[MVP-0]` THE SYSTEM SHALL redact known sensitive fields (`api_key`, `api_secret`, `signature`, `passphrase`, `oauth_token`) in all log paths (per `monitoring/logger.py`).
3. `[MVP-0]` THE SYSTEM SHALL maintain in-process gauges and counters (per `monitoring/metrics.py`) for: equity, exposure, risk_rejects, orders_emitted, runs_active, runs_failed, llm_calls, data_feed_staleness per source. `[v1]` `llm_calibration_score` (per task type) added when calibration tables ship.
4. `[MVP-0]` WHILE the engine is running THE SYSTEM SHALL emit PnL and exposure metrics at least every 30 seconds.
5. `[v1]` THE SYSTEM SHALL surface logs and metrics in the dashboard under a Diagnostics page, with filtering by run_id, severity, and event_type. `[MVP-0]` `/runs/[runId]` shows per-run logs and metrics; the broader Diagnostics page is `[v1]`.
6. `[MVP-0]` **Redis is transport, DuckDB is truth.** Every Redis Streams event SHALL be mirrored to a DuckDB row via the outbox pattern before any side effect commits. Consumers SHALL be idempotent by `(stream, event_id)` AND by the natural key of the payload (`client_id` for orders, `command_id` for chat commands, `decision_id` for risk decisions). Replaying the same Redis entry, or replaying the DuckDB row after a Redis flush, SHALL never produce a duplicate side effect. CI test `tests/integration/test_outbox_idempotency.py` injects a duplicate Redis entry and asserts at-most-once side effects.

#### Additional Details

- **Priority:** High **Complexity:** Low (existing scaffold has logger + metrics)
- **Dependencies:** Requirements 12, 31, 32.

---

### Requirement 42: Architecture Decision Records and System State Documentation

**User Story:** As the operator, I want a written record of architectural decisions and operational modes, so that future-me (and future agents) don't re-litigate settled questions.

#### Acceptance Criteria

1. THE SYSTEM SHALL maintain `DECISIONS.md` (already in scaffold) and append a new entry whenever an architectural decision is made or a default risk/promotion limit changes.
2. THE SYSTEM SHALL maintain a `SYSTEM_STATE.md` defining operational modes (`research | backtest | paper_trading | live_trading | paused`) and the transitions between them, with one diagram showing valid state transitions.
3. THE SYSTEM SHALL surface the current operational mode in the dashboard header.
4. WHEN an operational-mode transition occurs THE SYSTEM SHALL log `event="state_transition"` with `from`, `to`, `actor`, and `reason`.

#### Additional Details

- **Priority:** Medium **Complexity:** Low
- **Dependencies:** Requirements 24, 25.

---

### Requirement 43: Out of Scope (v1 Hard Boundaries)

**User Story:** As the operator, I want explicit hard boundaries, so that scope creep dies before it starts.

#### Acceptance Criteria

1. THE SYSTEM SHALL NOT ship in v1: a mobile native app; multi-user / per-user accounts; public sharing of runs/strategies; cloud deployment (AWS/GCP/Azure); tax-lot tracking or 1099-B export; options trading; HFT / sub-second latency; online-updating reinforcement-learning agents; auto-flipping live mode based on metrics; fully autonomous live trading without a manual enable switch; paid SaaS dependencies; 3rd-party strategy marketplaces; X/Twitter automated ingest (deferred to v2 due to free-tier constraints); voice or CLI chat surfaces.
2. WHERE an agent or operator proposes adding any item from 43.1 in v1 THE SYSTEM SHALL require a new spec session and a `DECISIONS.md` entry; agents alone SHALL NOT add such items.
3. THE SYSTEM SHALL NOT permit live trading of any asset class outside its execution scope (per Requirement 3.4–3.5) without a new spec session.

#### Additional Details

- **Priority:** High **Complexity:** Low (governance, not code)
- **Dependencies:** Requirements 3, 25.

---

### Requirement 44: Continuous Learning Across All Levers — Phased

**Phase tagging:** MVP-0 ships the foundation with the four levers
the reviewer recommended (strategy / source / feature / LLM-
calibration). The full lever-scoring scope (Q7 = full_levers) lands
during the v1 expansion. Auto-apply for non-risk levers is `[v1]`;
risk-sensitive levers stay advisory-only forever.

**User Story:** As the operator, I want every controllable dimension of the platform to be scored and adapted across runs, so that the system compounds an edge instead of ossifying around its initial configuration.

#### Acceptance Criteria

1. `[MVP-0]` THE SYSTEM SHALL maintain a learnable score for each of the following **MVP-0 lever classes**: data sources (`source_scores`), features (`feature_scores`), strategies (`strategy_scores`), and LLM judgment calibration (`llm_calibration`, per task type). `[v1]` THE SYSTEM SHALL extend lever scoring to: models (`model_scores`), universe membership (`universe_scores`), prompt versions (`prompt_scores`), slippage / cost estimates (`cost_model_scores`), alert thresholds, decision cadence parameters (`cadence_scores`), and risk-limit recommendations (`risk_advisory`, advisory only).
2. `[MVP-0]` WHEN a run completes THE SYSTEM SHALL update every applicable MVP-0 lever score using the run's measured outcomes, using the scoring rules defined in `design.md` § Learning Loop. `[v1]` Same, extended to all v1 lever classes.
3. `[MVP-0]` THE SYSTEM SHALL persist MVP-0 lever scores in DuckDB tables `source_scores`, `feature_scores`, `strategy_scores`, `llm_calibration` (per task type), each row stamped with `run_id`, `timestamp`, and `score_version`. `[v1]` Same for the v1 lever tables.
4. `[MVP-0]` THE SYSTEM SHALL expose MVP-0 lever scores at `/learnings` with a per-lever sparkline showing score evolution across the last N runs (configurable, default N=50). `[v1]` Same surface extended to all v1 lever classes.
5. `[v1]` IF a lever has accumulated `≥ run_count_threshold` (default 20) observations AND its score has crossed a configured promote/demote threshold THEN THE SYSTEM SHALL surface a `recommendations.json` entry proposing a config change. `[v1]` For non-risk levers (universe weight, prompt template, source weight) auto-apply is gated by per-lever `auto_apply_threshold` set in `configs/learning.yaml`. `[MVP-0]` All MVP-0 levers are advisory; no auto-apply in MVP-0.
6. `[MVP-0]` THE SYSTEM SHALL NOT silently mutate live-mode capital, risk limits, broker credentials, or kill-switch parameters as part of any learning update; those levers are advisory-only outputs in every phase.
7. `[MVP-0]` WHILE a lever has fewer than `min_observations` data points (default 5) THE SYSTEM SHALL mark its score as `insufficient_evidence` in the UI rather than emitting promote/demote recommendations.
8. `[v1]` WHERE the operator disables a specific lever class via the dashboard config THE SYSTEM SHALL stop scoring it but preserve historical scores for later re-enablement.
9. `[MVP-0]` THE SYSTEM SHALL feed every lever scorer **only out-of-sample (OOS) outcomes**: walk-forward holdout returns, purged-k-fold validation folds with embargo (`research/cv.py`), or paper-trading windows that post-date the data the lever influenced. THE SYSTEM SHALL forbid raw in-sample PnL, in-sample hit rate, or in-sample profit factor as score inputs. CI test `tests/learning/test_no_in_sample_scoring.py` SHALL parse each `Scorer.update()` implementation and assert it consumes only `RunSummary.oos_metrics.*` (or paper/live realised outcomes), never `RunSummary.in_sample_metrics.*`. _Rationale: `pocs/learning_feedback/run_poc.py` showed that raw IS PnL ranking inverts the order vs an injected edge with realistic noise; without an OOS rule, scoring amplifies noise._

#### Additional Details

- **Priority:** High **Complexity:** High
- **Dependencies:** Requirements 7, 8, 11, 13, 15, 16, 17, 22, 24, 26, 32, 33.
- **Assumptions:** Multi-armed-bandit logic uses an existing library (`mabwiser` or equivalent) rather than custom code, per Requirement 47.

---

### Requirement 45: Adaptive Performance and Self-Optimization

**User Story:** As the operator, I want the platform to know when it is slow or expensive, so that performance regressions become visible problems instead of slow leaks.

#### Acceptance Criteria

1. THE SYSTEM SHALL emit per-run telemetry covering: end-to-end run wall-clock time, ingest latency p95, decision-to-trade latency p95, LLM token spend (per provider), DB query p95, websocket reconnection count, and error rate, into the `run_metrics` table.
2. THE SYSTEM SHALL expose a `Diagnostics → Performance` dashboard page (per Requirement 35) that plots the metrics from 45.1 across the last 50 runs.
3. WHEN any metric in 45.1 crosses its configured budget for `≥ 3 consecutive runs` THE SYSTEM SHALL emit a `WARNING` notification (per Requirement 31) and add a `performance_regression` entry to the next run's `recommendations.json`.
4. THE SYSTEM SHALL ship default budgets matching the Performance non-functional section; budgets are editable from the dashboard.
5. IF the LLM token spend exceeds a configured monthly cap (default $20 if any paid provider is enabled) THEN THE SYSTEM SHALL fall back to Ollama and notify the operator (CRITICAL).
6. THE SYSTEM SHALL produce a quarterly self-optimization report listing the top three slowest pipeline stages and proposing concrete remediations (e.g., switch to Polars, increase DuckDB memory, parallelize ingest).
7. WHILE a run is degraded (45.3) THE SYSTEM SHALL continue to function correctly; degraded performance MUST NOT cause silent data loss or skipped decisions.

#### Additional Details

- **Priority:** Medium **Complexity:** Medium
- **Dependencies:** Requirements 31, 35, 41.
- **Assumptions:** Telemetry uses `monitoring.metrics` and `monitoring.logger`; no external APM SaaS in v1 (per Requirement 39).

---

### Requirement 46: Engineering Quality Bar (Production-Grade, No Shortcuts)

**User Story:** As the operator, I want every shipped change to meet a production-grade quality bar, so that technical debt does not erode the platform's trustworthiness over time.

#### Acceptance Criteria

1. THE SYSTEM SHALL forbid in shipped code: TODO / FIXME / XXX / HACK comments, stub functions returning placeholder data, unreachable / commented-out code, raise `NotImplementedError` in non-abstract paths, and `should work` / `left as an exercise` language in PR descriptions or docstrings (per `.cursor/rules/pr-review.mdc`).
2. THE SYSTEM SHALL enforce 46.1 in CI via a custom `ruff` ruleset and a regex-based grep job; violations fail the build.
3. THE SYSTEM SHALL require every public function and class in `data/`, `research/`, `strategies/`, `risk/`, `execution/`, `monitoring/`, and `backend/api/` to carry a complete docstring including Args, Returns, Raises, and Example.
4. THE SYSTEM SHALL require type annotations enforced by `mypy --strict`; the build fails on any `Any`, `# type: ignore`, or untyped function unless the line is annotated with a `# noqa: justified-by=...` comment that cites a `DECISIONS.md` entry.
5. THE SYSTEM SHALL aim for quality tests over quantity. Every test MUST assert an observable, externally meaningful behavior; tests-for-coverage-only, snapshot-only tests of trivial markup, and assertions that merely re-state the implementation are forbidden.
6. THE SYSTEM SHALL require test coverage on **key components and tools** as the primary target — specifically: `risk.engine`, `risk.sizing`, every Broker adapter, the run orchestrator, the learning-loop scorers, the deterministic backtest harness, every public API route, the LLM client and isolation tests, and every exported frontend component (per Requirement 50.4). Lower-value paths (config glue, trivial getters, framework wiring) MAY remain untested if they have no behavior worth asserting.
7. THE SYSTEM SHALL define test categories explicitly in `design.md` § Testing Strategy: unit (pure functions), integration (cross-module contracts), e2e (full pipeline smoke), property (hypothesis-based on numeric paths where applicable), security (LLM isolation, no-bypass-flag, gitleaks), and frontend component tests against styleguide demo data (per Requirement 50).
8. WHEN a PR introduces a key component or tool from 46.6 THE SYSTEM SHALL require at least one quality test exercising its public contract; the PR description MUST link the test and explain what behavior it locks in.
9. THE SYSTEM SHALL mark a task `partial` in the spec if any acceptance criterion is unmet; `partial` tasks MUST NOT be merged to `main` without an explicit `DECISIONS.md` waiver.
10. THE SYSTEM SHALL require all configs, schemas, and protocols to be Pydantic-validated at boundary; raw `dict` arguments are forbidden in cross-module APIs.
11. WHERE a test exists primarily to satisfy a coverage tool THE SYSTEM SHALL delete it; coverage is a side-effect of valuable tests, not a goal.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 23 (Security/CI), 41 (Observability), 47 (Library-first).
- **Source authority:** `.cursor/rules/pr-review.mdc`, `.cursor/rules/coding-standards.mdc`.

---

### Requirement 47: Library-First and MCP-First Implementation

**User Story:** As the operator, I want the platform built from well-maintained libraries and MCP servers wherever possible, so that we minimize custom code surface area and maximize correctness inherited from the ecosystem.

#### Acceptance Criteria

1. THE SYSTEM SHALL prefer existing Python packages, MCP servers, and proven OSS components over custom code for: HTTP clients (`httpx`), retries (`tenacity`), config (`pydantic-settings`), logging (`structlog`), CLI (`click` or `typer`), exchange access (`ccxt`), backtests (`vectorbt`), feature engineering (`pandas-ta`, `talib-binary`), ML (`lightgbm`, `xgboost`, `scikit-learn`, `pytorch`), experiment tracking (`mlflow`), bandits (`mabwiser`), DB (`duckdb` + `pyarrow`), API (`fastapi` + `uvicorn`), pub/sub (`redis`), frontend (`next`, `tailwindcss`, `shadcn/ui`, `tradingview-lightweight-charts`, `tanstack-table`), and LLM provider abstraction (`litellm` or first-party SDKs).
2. THE SYSTEM SHALL document every chosen library with version pin, license, and last-updated date in `pyproject.toml` / `package.json`, and review pins quarterly.
3. WHEN an agent or operator proposes writing custom code that duplicates an existing library or MCP capability THE SYSTEM SHALL require a `DECISIONS.md` entry justifying the decision; otherwise the agent MUST use the library.
4. THE SYSTEM SHALL prefer Cursor MCP servers (per `.cursor/mcp.json`: `duckdb`, `ccxt`, `github`, `playwright`, `filesystem`, `shell`, `docs`, `sequential-thinking`, `web-fetch`) over reimplementing those capabilities in agent code.
5. WHERE no maintained library or MCP exists THE SYSTEM MAY produce custom code, but only after an explicit web-research step (per Requirement 48) confirms no off-the-shelf solution.
6. THE SYSTEM SHALL forbid the rebuild of any subsystem already covered by an existing library unless `DECISIONS.md` records: (a) the surveyed alternatives, (b) the disqualifying criteria, (c) the maintenance owner.
7. THE SYSTEM SHALL keep a `LIBRARIES.md` index mapping each domain (ingest, features, models, backtest, etc.) to the chosen library and the rejected alternatives, refreshed whenever a library is added or removed.

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 23, 25, 48.
- **Assumptions:** All libraries used are free / OSS-licensed (per Requirement 39).

---

### Requirement 48: Web Research Before Implementation

**User Story:** As the operator, I want every implementation task to begin with current web research, so that the platform reflects the state of the art rather than stale knowledge.

#### Acceptance Criteria

1. WHEN an agent begins implementing any non-trivial task (new feature, new strategy archetype, new ingest source, new broker adapter, new model, new dashboard page, or any task tagged `research-required` in `tasks.md`) THE SYSTEM SHALL require a documented web-research step using the `web-fetch` MCP, the `docs` MCP, or the built-in `WebSearch` tool before code is written.
2. THE SYSTEM SHALL store the research output as a markdown note under `specs/<feature-name>/research/<task-id>.md` containing: query, sources consulted (URL + retrieval date), summary of findings, chosen approach, and rejected alternatives.
3. THE SYSTEM SHALL require the research note to cite at least one source dated within the last 12 months OR explain why older sources are still authoritative.
4. WHEN consulting library documentation THE SYSTEM SHALL prefer the official docs (e.g., the `docs` MCP, the project's GitHub README, ReadTheDocs) over secondary blog posts or aggregator sites.
5. WHERE the research surfaces a library, MCP, or pattern that already solves the problem THE SYSTEM SHALL adopt it unless a `DECISIONS.md` entry justifies otherwise (per Requirement 47.6).
6. THE SYSTEM SHALL forbid implementation tasks from skipping the research step on the rationale that "the agent already knows"; agents must reset to current docs.
7. THE SYSTEM SHALL attach the research note path to every PR description for a `research-required` task.

#### Additional Details

- **Priority:** High **Complexity:** Low
- **Dependencies:** Requirements 47, 49.
- **Assumptions:** Network access to public documentation is available; if it isn't, the task is blocked rather than executed without research.

---

### Requirement 49: Cursor Harness Use Mandate

**User Story:** As the operator, I want every implementation task to use the Cursor agent harness (rules, agents, skills, hooks, MCPs), so that the project's governance is enforced consistently and the harness investment compounds.

#### Acceptance Criteria

1. THE SYSTEM SHALL require all multi-file feature implementations to be performed within a Cursor spec session, per `.cursor/rules/spec-sessions.mdc`.
2. WHEN executing implementation tasks THE SYSTEM SHALL prefer the domain subagents under `.cursor/agents/` (`research`, `signal`, `strategy`, `backtest`, `risk`, `evaluation`, `monitoring`, `reviewer`, `planner`, `developer`) over generic `generalPurpose` for matching domain work.
3. WHEN tasks match a defined skill in `.cursor/skills/` (`session-init`, `research-signal`, `run-backtest`, `evaluate-strategy`, `promote-strategy`, `docker-build`, `orchestrate`, `review-local`, `script-first-python`) THE SYSTEM SHALL invoke that skill at the start of the task.
4. THE SYSTEM SHALL run all configured `.cursor/hooks/` hooks during agent operation; agents MUST NOT bypass hooks (no `--no-hooks`, no manual hook disabling).
5. THE SYSTEM SHALL invoke the configured MCP servers (per `.cursor/mcp.json`) for every capability they cover (DuckDB queries, CCXT exchange calls, GitHub operations, Playwright browser checks, filesystem reads, shell, docs, sequential-thinking, web-fetch).
6. WHEN a session ends THE SYSTEM SHALL append a `SESSION_LOG.md` entry per `.cursor/rules/workflow.mdc`.
7. WHERE a Cursor rule, agent, skill, hook, or MCP needs to change THE SYSTEM SHALL require the change to be proposed via the reviewer agent and ratified by a `DECISIONS.md` entry; agents MUST NOT silently edit files under `.cursor/rules/`.
8. THE SYSTEM SHALL forbid LLM use in `execution/` directly or transitively per `.cursor/rules/llm-usage.mdc`; CI test `tests/security/test_llm_isolation.py` enforces this.

#### Additional Details

- **Priority:** High **Complexity:** Low
- **Dependencies:** Requirements 23, 46, 47, 48.
- **Source authority:** `.cursor/rules/spec-sessions.mdc`, `.cursor/rules/ai-workflow.mdc`, `.cursor/rules/workflow.mdc`, `AGENTS.md`.

---

### Requirement 50: Style Guide and Component Library (Component-First UI)

**User Story:** As the operator and any future contributor, I want every UI component documented, demoable, and testable in isolation on a styleguide page before it lands in any product page, so that the frontend stays consistent, reusable, and visually testable without spinning up the full backend.

#### Acceptance Criteria

1. THE SYSTEM SHALL provide a `/styleguide` route in the Next.js dashboard that lists every component the platform uses, grouped by category (primitives, data, charts, navigation, feedback, forms, run-specific, AI surfaces, dashboard widgets).
2. THE SYSTEM SHALL render each component on the styleguide with: component name, source path, prop table generated from TypeScript types, at least one demo state (default), additional demo states covering empty / loading / error / populated where applicable, accessibility notes (ARIA roles, keyboard interactions), and a "copy import path" affordance.
3. THE SYSTEM SHALL drive every styleguide demo from local mock data fixtures stored under `frontend/styleguide/mocks/<component-name>.ts`; styleguide demos MUST NOT depend on the backend or any live network call.
4. WHEN a developer or agent introduces a new component THE SYSTEM SHALL require its styleguide entry to land in the same PR; PRs that add a component but no styleguide entry are rejected. A pre-commit check (Cursor hook or `husky`-managed `lint-staged`) MUST enforce this on `frontend/components/**/*.tsx`.
5. WHEN a developer or agent uses a component on a product page THE SYSTEM SHALL require that the component already exists in the styleguide; CI fails if a page imports a component path that has no styleguide entry. The "component-first" order is: **styleguide entry → component implementation → product page usage**, never the reverse.
6. THE SYSTEM SHALL keep the styleguide self-contained: it MUST run via `npm run dev` with no other services, and MUST render correctly with `BACKEND_URL=` unset.
7. THE SYSTEM SHALL provide a "Run component tests" affordance on each styleguide entry: clicking it executes the component's frontend tests (Vitest + React Testing Library) against the same mock fixtures used for the demo. Test results MUST display inline in the styleguide.
8. THE SYSTEM SHALL require every component to be reusable and modular: components MUST NOT hard-code colors, copy strings, or business logic; styling is via Tailwind tokens defined in `frontend/styles/tokens.css`; copy strings live in `frontend/i18n/<locale>.json` (`en` only in v1).
9. THE SYSTEM SHALL ship a component checklist enforced by a Cursor rule (`.cursor/rules/component-first.mdc`) covering: TypeScript types exported, props documented, mock fixture present, a11y reviewed, dark-mode supported, responsive at `sm/md/lg/xl`, no inline `fetch`.
10. THE SYSTEM SHALL surface a "Component Status" badge on every styleguide entry: `draft | reviewed | production`. Only `production` components MAY be used on the operator-facing pages of the dashboard; `draft` and `reviewed` are styleguide-only.
11. WHERE a third-party component (`shadcn/ui`, `tradingview-lightweight-charts`, `tanstack-table`) is used THE SYSTEM SHALL still publish a wrapper entry in the styleguide documenting the project-specific defaults, props, and demo data, in line with Requirement 47 (library-first).

#### Additional Details

- **Priority:** High **Complexity:** Medium
- **Dependencies:** Requirements 33, 34, 35, 46, 47, 49.
- **Existing assets:** `frontend/components/ui/{badge,card,input,table}.tsx`, `frontend/components/charts/equity-chart.tsx`, `frontend/components/data/trades-table.tsx`, `frontend/components/nav/{header,sidebar}.tsx` are the v1 baseline that MUST be backfilled into the styleguide on first delivery.
- **Tooling:** Use `react-docgen-typescript` or equivalent for the prop table; do not hand-write prop documentation. Use `@storybook/test-runner` or Vitest for the inline test runner; pick the lighter option, prefer existing OSS over custom.
- **Cursor harness wiring (per Requirement 49):** ship `.cursor/rules/component-first.mdc`, a `.cursor/skills/styleguide-add-component/SKILL.md`, and a `beforeWriteFile` hook under `.cursor/hooks/component_first.py` that blocks writes to `frontend/components/**/*.tsx` when no matching styleguide entry exists.

---

### Requirement 51: Coding Standards, Contribution Guide, and Cursor-Harness Enforcement

**User Story:** As the operator and any future contributor, I want a single canonical coding standard and contribution guide, enforced consistently by both human review and the Cursor harness, so that any contributor (human or agent) can ship a quality change without inventing process.

#### Acceptance Criteria

1. THE SYSTEM SHALL maintain `docs/CODING_STANDARDS.md` (already present) as the canonical coding standard, plus `.cursor/rules/coding-standards.mdc` (already present) as the always-applied agent-facing version. The two MUST stay in sync; CI fails if their content drifts beyond a documented allow-list.
2. THE SYSTEM SHALL ship a `CONTRIBUTING.md` at the repo root covering: how to set up the dev environment, how to run tests/lint/typecheck, branch naming, commit format (Conventional Commits per `.cursor/rules/commit-conventions.mdc`), PR template, the spec-session protocol (per `.cursor/rules/spec-sessions.mdc`), the Definition of Done, the styleguide-first rule (Requirement 50.4–5), the library-first rule (Requirement 47), the web-research rule (Requirement 48), the no-shortcuts rule (Requirement 46), and how to file a `DECISIONS.md` entry.
3. THE SYSTEM SHALL ship `.github/pull_request_template.md` enforcing the format from `.cursor/rules/pr-review.mdc`: What changed (1–5 bullets), Verification performed (commands run + results), Risks / edge cases, Linked spec / requirement IDs, Linked styleguide entries (for frontend changes), Linked research note (for `research-required` tasks).
4. THE SYSTEM SHALL ship `.github/ISSUE_TEMPLATE/{bug.md,feature.md,research.md}` matching the spec-session triggers in `.cursor/rules/spec-sessions.mdc`.
5. THE SYSTEM SHALL ship pre-commit hooks (via `pre-commit` or `husky` + `lint-staged`) that run: `ruff check`, `ruff format --check`, `mypy --strict`, frontend `eslint`, frontend `tsc --noEmit`, the no-shortcuts grep from Requirement 46.2, the no-risk-bypass grep from Requirement 23, and the styleguide-first check from Requirement 50.4. Pre-commit MUST be the same set of checks CI runs.
6. THE SYSTEM SHALL bake the standards into the Cursor harness, in line with Requirement 49: any process described in `CONTRIBUTING.md` SHALL also be expressed as one or more of `.cursor/rules/*.mdc` (always-on guidance), `.cursor/agents/*.md` (subagent role), `.cursor/skills/*/SKILL.md` (procedural how-to), or `.cursor/hooks/*.py` (deterministic enforcement).
7. THE SYSTEM SHALL keep `CONTRIBUTING.md` and the `.cursor/` harness as the single source of process truth: ad-hoc process docs scattered across the repo are forbidden; if process needs updating, update those files (and `DECISIONS.md` when an architectural decision shifts).
8. WHEN an agent or human runs `pytest` / `ruff` / `mypy` / frontend `npm test` THE SYSTEM SHALL emit zero warnings unless the warning has a `# justified-by=<DECISIONS-id>` comment. Unjustified warnings fail CI.
9. THE SYSTEM SHALL provide a `make help` (or equivalent npm/pnpm script) listing every common contributor command: `setup`, `lint`, `format`, `typecheck`, `test`, `test-fast`, `test-frontend`, `styleguide`, `backtest-smoke`, `run-up`, `run-down`, `clean`. The list MUST be discoverable from `CONTRIBUTING.md`.
10. THE SYSTEM SHALL keep a `LIBRARIES.md` index (per Requirement 47.7) cross-referenced from `CONTRIBUTING.md` so contributors choose the right library before writing code.
11. THE SYSTEM SHALL document the agent-specific contribution loop: which subagent to invoke for which task type (per Requirement 49.2), which skill to start with (per Requirement 49.3), and how to attach research notes (per Requirement 48.7) in `CONTRIBUTING.md` § "Contributing as an AI agent".

#### Additional Details

- **Priority:** High **Complexity:** Low
- **Dependencies:** Requirements 23, 46, 47, 48, 49, 50.
- **Existing assets:** `docs/CODING_STANDARDS.md`, `.cursor/rules/coding-standards.mdc`, `.cursor/rules/pr-review.mdc`, `.cursor/rules/commit-conventions.mdc`, `AGENTS.md`, `WORKFLOW.md`. These MUST be the building blocks; no parallel docs.
- **Cursor harness wiring (per Requirement 49):** add `.cursor/skills/contribute/SKILL.md` (the agent contribution loop), `.cursor/hooks/pr_template_check.py` (verifies PR descriptions match the template), and ensure existing `block_dangerous_shell.py`, `guard_mcp_writes.py`, `guard_risk_files.py`, `format_python.py` remain enforced.

---

## Non-Functional Requirements

### Performance

1. WHILE a run is executing THE SYSTEM SHALL deliver decision/trade events to the run page within `≤ 500 ms` p95 of internal emission.
2. WHEN the API receives a `GET /api/runs/<id>` request THE SYSTEM SHALL respond within `≤ 250 ms` p95.
3. WHEN running a backtest over 100,000 bars THE SYSTEM SHALL complete in under 60 seconds on a single core.
4. WHEN the dashboard loads any page THE SYSTEM SHALL render the first contentful paint within `≤ 1.5 s` on the operator's local network.
5. WHEN the LLM run-retrospective summary is generated THE SYSTEM SHALL complete within `≤ 2 minutes` for a 1-hour run on the configured local model; if exceeded, a deterministic fallback per Requirement 12.4 SHALL be produced.

### Reliability

1. WHEN an upstream exchange disconnects THE SYSTEM SHALL retry with exponential backoff for at most 5 attempts, then transition the run to `degraded` and emit a CRITICAL `data_feed_stale` alert.
2. IF a partial fill is reported by a broker THEN THE SYSTEM SHALL reconcile the local position before placing further orders.
3. WHEN the trading-engine container restarts THE SYSTEM SHALL recover or fail-safely transition every previously-running run, with no silent loss.
4. THE SYSTEM SHALL achieve `≥ 99%` uptime for paper-mode runs over any rolling 30-day window after v1 launch.

### Security

1. THE SYSTEM SHALL load all API keys (Binance, Coinbase, Alpaca, Schwab, OpenAI, Anthropic) from environment variables only; THE SYSTEM SHALL NOT log raw key material.
2. WHERE the call path is `execution/*` THE SYSTEM SHALL NOT import any module under `research.llm` (per `.cursor/rules/llm-usage.mdc`).
3. THE SYSTEM SHALL route every order — backtest, paper, or live — through `risk.engine.RiskEngine.check_and_size`. CI SHALL grep for forbidden bypass flags (`skip_risk`, `bypass_risk`, `RISK_BYPASS`, `DISABLE_RISK`, `--no-risk`) and fail builds that introduce them.
4. THE SYSTEM SHALL run all containers as non-root users (per existing Dockerfiles).
5. THE SYSTEM SHALL NOT permit committed secrets; CI SHALL run `gitleaks` on every PR.
6. THE SYSTEM SHALL pin exchange/broker hostnames in code; THE SYSTEM SHALL NOT build hostnames from operator input.

### Observability

1. WHEN any order is rejected by risk THE SYSTEM SHALL emit a structured log with `event="risk_reject"` and the rejection reason.
2. WHILE the engine is running THE SYSTEM SHALL emit PnL and exposure metrics at least every 30 seconds.
3. THE SYSTEM SHALL emit `event="run_started"`, `event="run_ended"`, `event="run_failed"` for every run lifecycle transition.
4. THE SYSTEM SHALL emit `event="llm_call"` for every LLM invocation with prompt name + version, provider, model, token counts, redacted prompt hash.
5. THE SYSTEM SHALL surface a Diagnostics page listing the last `N` metrics snapshots and recent logs, filterable by run, severity, event_type.

### Determinism

1. WHEN given the same `(strategy_version, dataset_version, feature_set_version, parameters, git_commit, seeds, cost_model_version)` THE SYSTEM SHALL produce byte-identical `metrics.json` output.
2. THE SYSTEM SHALL set explicit numpy and torch seeds in every backtest and training run; THE SYSTEM SHALL persist them in the run manifest.
3. THE SYSTEM SHALL ensure the run-retrospective LLM summary is treated as **non-deterministic output** (its content is not part of the determinism guarantee); all numerical artifacts (`metrics.json`, `trades.jsonl`) SHALL remain deterministic.

### Resilience

1. THE SYSTEM SHALL implement circuit-breaker semantics on every external boundary: after `N` consecutive failures (default 5) within `T` seconds (default 60), the boundary SHALL open and skip calls for `T_cool` seconds (default 300).
2. WHEN a circuit opens THE SYSTEM SHALL emit a WARNING alert and continue runs with the affected source marked `degraded`.
3. WHEN a circuit recovers THE SYSTEM SHALL emit an INFO alert and resume normal operation.

---

## Constraints and Assumptions

### Technical Constraints

- Python 3.11+, `mypy --strict`, `ruff` (line length 100) per `.cursor/rules/coding-standards.mdc`.
- DuckDB is the canonical data store; new persistence layers require a `DECISIONS.md` entry.
- All cross-module data contracts use Pydantic models or typed DataFrames per `.cursor/rules/architecture.mdc`.
- Module imports must respect the one-way pipeline: `data → research → strategies → risk → execution`.
- Money is `Decimal` at any broker boundary; floats inside research only.
- Timestamps are timezone-aware `pd.Timestamp(tz="UTC")`.
- Existing scaffold's risk engine (`risk/engine.py`), backtest engine (`backtests/engine.py`), feature validators (`research/features/validation.py`), LLM isolation test (`tests/security/test_llm_isolation.py`) MUST remain in place.

### Business Constraints

- Per-strategy live capital cap from dashboard config (default $1,000 total) — features must not assume larger budgets.
- Free-only stack per Requirement 39 — no paid SaaS in v1.
- Single-operator, semi-serious side-project (~2 hr/day) — feature complexity must respect this maintenance budget.
- Solo operator running on a single Unraid box with one RTX 3090 / 24GB VRAM.

### Assumptions

- Operator's Unraid host is always-on with reliable backup of the appdata mount.
- Network is generally reliable but transient outages occur and must be handled.
- Operator has minimal trading background, so the UI must teach.
- Operator has admin/code access to the box; multi-user auth is not required in v1.
- Existing Cursor harness (`.cursor/rules/`, `.cursor/agents/`, `.cursor/hooks/`, `.cursor/scripts/spec-new.js`, `.cursor/spec-templates/`) remains the governance layer and is not rewritten by this spec.

---

## Success Criteria

### Definition of Done

- [ ] All acceptance criteria for every functional requirement are met.
- [ ] All non-functional requirements are met or have a `DECISIONS.md`-recorded waiver.
- [ ] `pytest -q`, `ruff check .`, `mypy --strict .`, and AI-eval gates are green.
- [ ] At least one e2e test exercises a `MarketScoutRun` end-to-end on synthetic + real data.
- [ ] The v1 acceptance test in Requirement 1.2 reproducibly succeeds with no operator intervention beyond Start and Approve.
- [ ] `SESSION_LOG.md` entry added.
- [ ] `DECISIONS.md` entries for any default-limit changes from the existing scaffold.

### Acceptance Metrics

- Run a 1-hour `MarketScoutRun` on default config; the artifact folder contains all 8 canonical files (Requirement 12.1) and `summary.md` is non-empty.
- Trigger each of the 7 must-have alerts via test fixtures; all 7 route to the correct channels with correct severity.
- Run a backtest twice with identical inputs; `metrics.json` is byte-identical.
- LLM-isolation CI test passes: `execution/*` does not import `research.llm`.
- Risk-bypass-flag grep CI step passes: no forbidden flag string is present.
- Dashboard loads every primary page (`/`, `/runs`, `/runs/[id]`, `/strategies`, `/signals`, `/backtests`, `/insights`, `/chat`, `/health`, `/diagnostics`) without error and shows non-mocked data once a run has executed.
- A simulated kill-switch breach cancels all open paper orders, sets `live_mode_enabled = false` (already false), and emits a CRITICAL alert.
- Schwab read-only Portfolio Review Run produces a written recommendation classified as `insight_only`.
- Insight Intake accepts a sample paste, returns the structured schema with `trade_allowed = false`, and persists the artifact.

---

## Glossary

| Term | Definition |
| --- | --- |
| Run | An asynchronous, configurable market-intelligence experiment with isolated state and a frozen config snapshot. |
| RunConfig | The frozen configuration of a run, capturing duration, mode, universe policy, sources, decision policy, risk profile, learning policy, notification policy. |
| R-state | A strategy's position on the evidence ladder: `X | R0 | R1 | R2 | R3 | R4 | R5`. |
| Insight Intake | The dashboard surface accepting pasted text or links, returning a structured market interpretation classified as `insight_only` in v1. |
| Confirmation Tier | The minimum source-evidence required to classify an insight: insight-only (1 source), paper-trade (2 sources or 1 + price/volume), live (multi-source + R3 strategy + risk + permission). |
| Approval Queue | The dashboard surface showing AI-proposed approval-required changes pending operator action. |
| Per-run / Experiment / Global memory | The three explicit memory layers separating ephemeral per-run state, aggregated experiment-type metrics, and approved-only global learnings. |
| Bandit allocation | Multi-armed bandit policy used to balance exploration of new symbols against exploitation of proven ones in adaptive universe selection. |
| Kill switch | The platform-wide hard stop that cancels open orders, halts running live runs, sets `live_mode_enabled = false`, and requires operator action to clear. |
| Deflated Sharpe | Sharpe ratio adjusted for the number of trials run, used to detect spurious backtest edges. |
| MLflow-style experiment store | An experiment tracking pattern (loosely after MLflow) that records run parameters, metrics, artifacts, and start/end times to a queryable store. |
| LLM Calibration Score | Empirical reliability of LLM declared confidence over a rolling window, computed by comparing confidence buckets to realized outcomes. |
| Live-Enablement Gate | The six-condition check that must all pass before any live order can be placed (Requirement 4.3). |
| Operational mode | One of `research | backtest | paper_trading | live_trading | paused`, surfaced in the dashboard header (Requirement 42.3). |
| Lever | Any controllable, scoreable dimension of the platform whose configuration can be adapted across runs (sources, features, strategies, models, universe, prompts, cadence, cost models, alert thresholds, advisory risk settings). See Requirement 44. |
| Guiding Principles | The 26 cross-cutting principles in the Introduction that every requirement, design choice, and implementation task must respect. |
| Library-first | Engineering rule (Requirement 47) that prefers proven OSS packages and MCP servers over custom code; deviations require `DECISIONS.md`. |
| Research-required task | A `tasks.md` task tagged with `research-required` that must produce a `specs/<feature>/research/<task-id>.md` note before code is written (Requirement 48). |
| Cursor harness | The collection of `.cursor/rules/`, `.cursor/agents/`, `.cursor/skills/`, `.cursor/hooks/`, and `.cursor/mcp.json` that governs agent behavior on this project (Requirement 49). |
| Styleguide | The `/styleguide` route in the Next.js dashboard that documents and demoes every component the platform uses, with mock data, prop tables, accessibility notes, and inline component tests (Requirement 50). |
| Component-first | The delivery order rule: a component MUST appear in the styleguide before it is used in any product page (Requirement 50.5). |
| Component Status | Per-component badge `draft | reviewed | production`; only `production` components are allowed on operator-facing dashboard pages (Requirement 50.10). |
| Quality tests over quantity | Testing posture: tests target key components and tools and assert observable behavior; coverage-only tests are forbidden (Requirements 46.5–46.8, 46.11). |
| Contribution loop | The canonical procedure (human and agent) for landing a change in the repo, defined by `CONTRIBUTING.md` plus the `.cursor/` harness (Requirement 51). |

---

## Requirements Review Checklist

Run before marking Phase 1 approved:

### Completeness

- [ ] Every user story has role + functionality + benefit.
- [ ] Every requirement has at least one EARS acceptance criterion.
- [ ] Non-functional requirements covered (perf, reliability, security, observability, determinism, resilience).
- [ ] Success metrics are quantitative.

### EARS validity

- [ ] Every criterion uses WHEN / IF / WHILE / WHERE or is ubiquitous.
- [ ] Every criterion ends with `THE SYSTEM SHALL <verb>`.
- [ ] No vague adjectives ("fast", "user-friendly", "robust").

### Traceability

- [ ] Requirements are numbered (`Requirement 1` … `Requirement 51`).
- [ ] Each requirement traces back to one or more of the 26 Guiding Principles in `design.md` § Requirement Traceability.
- [ ] Every frontend component named in design.md is also named in the styleguide plan (Requirement 50).
- [ ] `CONTRIBUTING.md`, `docs/CODING_STANDARDS.md`, and `.cursor/` harness assets are listed as deliverables in tasks.md (Requirement 51).
- [ ] Acceptance criteria within each requirement are numbered (`1.1`, `1.2`, …) so `tasks.md` can cite them as `_Requirements: 1.2, 3.1_`.
- [ ] Dependencies between requirements are explicit in each requirement's Additional Details.

### Project alignment

- [ ] Compatible with `.cursor/rules/architecture.mdc` (one-way pipeline, non-bypassable risk, no look-ahead, configs over code).
- [ ] Compatible with `.cursor/rules/security.mdc` (no secrets, no LLM in trading path, env-var-loaded keys).
- [ ] Compatible with `.cursor/rules/coding-standards.mdc` (typing, decimals for money, UTC timestamps).
- [ ] Compatible with `.cursor/rules/risk-management.mdc` (kill switch, dashboard-tunable limits, no bypass flags).
- [ ] Compatible with `.cursor/rules/llm-usage.mdc` (LLM research-only, never on the trading path).
- [ ] Compatible with `AGENTS.md` agent definitions and per-agent LLM allowlist.

---

> **Next phase:** when this document is approved, fill in `./design.md` from
> `.cursor/spec-templates/design-template.md`. The design phase will translate
> these 51 functional requirements + 5 non-functional sections + 26 Guiding
> Principles into concrete components, interfaces, data models, API contracts,
> error handling, testing strategy, and deployment notes — citing requirement
> numbers and principle numbers throughout.
