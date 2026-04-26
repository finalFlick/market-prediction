# TODO — Sprint 1: Foundation

Goal: end the sprint with the full pipeline runnable end-to-end on one symbol
(BTCUSDT, 1h bars, 1 year of history) using a baseline LightGBM signal, in
paper-trading mode, with monitoring.

Definition of done for the sprint: `python -m execution.runner --broker paper`
trades for 24h on the baseline strategy without errors and writes a coherent
monitoring report.

Spec execution roadmap: `specs/trading-lab-platform/tasks.md` now indexes the
production task system for the broader platform build. Use its epic/feature
tickets as the source of truth when splitting implementation work; keep this
sprint checklist as the narrow foundation slice.

## 2026-04-26 status addendum

Completed (landed in `main`):

- [x] **FEATURE-0045** — Neko Quant identity layer (additive):
  `frontend/components/identity/*`, voice lib, Swagger watermark, DEC-011/012,
  docs. Does **not** touch the paused styleguide agent’s untracked WIP paths.
  Follow-ups: FEATURE-0046–0049 (mascot motion, SFX, hacker terminal, achievements).

## 2026-04-26 status addendum (historical)

Completed (landed in `main`):

- [x] Fast Docker dev loop: `Dockerfile.base`, `Dockerfile.research`,
  `docker-compose.dev.yml`, `dev.py`, and docs. Windows bind-mount masks are
  required for usable pytest performance.
- [x] MVP-0 run visibility slice: run list/detail/compare pages, learning
  scoreboard page, run API filters, learning compare/scoreboard API, SSE replay
  endpoint, and run worker tests.
- [x] Cursor harness docs/rules update: component-first rule, frontend/docker
  rule improvements, prompt-context-router docs correction, and routing updates.
- [x] Styleguide source ticket strengthened:
  `specs/trading-lab-platform/tasks/frontend-operator-experience/style_guide_component_library_0034.md`
  is now build-ready guidance.
- [x] PR #3 — `chore(github): public-repo governance, CI hardening, and spec
  addenda`. Merged at `a96280f`. Adds Dependabot, CodeQL, CODEOWNERS,
  composite Python CI setup, fork-PR threat-model docs, branch protection,
  and `next` 14→15.5.15 / `postcss` ^8.5.10 dep bumps. Six required checks
  green on `main`. (See `SESSION_LOG.md` for details.)
- [x] PR #17 — `ci(docker): build trading-base before service images and
  publish to GHCR`. Merged at `8174b0b`. Adds `trading-base` build step in
  the `docker` job, a separate `trading-base.yml` workflow that publishes
  `ghcr.io/<owner>/trading-lab-base:<sha>` on `main`, switches buildx to
  the `docker` driver so `FROM trading-base` resolves locally between steps,
  and adds `frontend/public/.gitkeep` to fix a pre-existing Dockerfile copy
  bug. The `docker · build images` job is now green on `main`. Trade-off
  recorded in `.github/workflows/ci.yml`: `docker` driver does not support
  `cache-from: type=gha`, so trading-base does a cold pip install each PR
  run (~3-5 min). Warm registry cache via `trading-base.yml` is a follow-up.

Immediate follow-ups:

- [x] **FEATURE-0034** styleguide Mocha rebuild + registry (`feat/styleguide-mocha`).
  `9913a86` (`frontend-init` Compose) is cherry-picked on `main` locally; open
  PRs: (A) `main` with init commit, (B) styleguide from `feat/styleguide-mocha`.
- [ ] Run full global gates on the merged result (`pytest -q`, `ruff check .`,
  `mypy --strict .`, frontend lint/typecheck/build, e2e, backtest smoke) before
  deleting `backup/chore-gov-pre-slim` / popping `stash@{0}`.
- [x] `9913a86` — cherry-picked onto local `main` (2026-04-26). Push/PR when ready.

## Agent Coordination

**2026-04-26 — resolved:** FEATURE-0034 Mocha + Neko rebuild is implemented on
`feat/styleguide-mocha`. `9913a86` (`frontend-init`) is cherry-picked on local
`main`. Do **not** delete `backup/chore-gov-pre-slim` or pop `stash@{0}` until
the owner merges and approves.

### Remaining (non-blocker)

- [ ] **Open / squash-merge PR for `feat/styleguide-mocha`** (pushed
  2026-04-26 15:50). After merge, update FEATURE-0034 addendum with the
  `main` merge SHA, then optionally retire `backup/chore-gov-pre-slim`.
- [x] **Ratified DEC-014** — workflow.mdc (self-SHA + PowerShell commit
  recipe) + frontend.mdc (`lightweight-charts` jsdom mocking).
- [ ] **Triage open Dependabot PRs** — PR #9 (postcss), PR #13 (next 16 + React
  19), PR #16 (vite/vitest 4). PR #15 closed as duplicate of PR #16.
- [ ] **Postcss alert #7** — until `overrides.postcss = "^8.5.10"` or a newer
  bundled `next` postcss.
- [ ] **Drop local-only refs** `pr-13`, `pr-15`, `pr-16` if still present.

### Handoff (future agents)

1. Read the latest `SESSION_LOG.md` after this file.
2. **Spec** — `specs/trading-lab-platform/tasks.md` Wave 1.
3. **Risk** — non-bypassable; see `DECISIONS.md` DEC-002 and `risk/engine.py`.
4. **CI** — same six checks + `docker · build images` as on `main`.

---

## Milestone 1 — Data layer

- [ ] `data/ingest/binance.py`: REST historical klines + websocket live trades.
- [ ] `data/ingest/coinbase.py`: REST historical candles + websocket ticker.
- [ ] `data/store.py`: DuckDB-backed OHLCV store with idempotent upserts.
- [ ] `data/ingest/run.py` CLI: `--exchange --symbol --timeframe --days`.
- [ ] Unit tests for the store and CLI argument parsing.
- [ ] One year of BTCUSDT 1h klines materialized in DuckDB.

## Milestone 2 — Feature pipeline

- [ ] `research/features/price.py`: returns, log-returns, rolling vol, z-scores.
- [ ] `research/features/volume.py`: dollar volume, volume z-score, OBV.
- [ ] `research/features/momentum.py`: MA crossovers, RSI, MACD.
- [ ] `research/features/validation.py`: shift-check + schema validator.
- [ ] `research/labels.py`: forward log-return + triple-barrier labels.
- [ ] `research/features/build.py` CLI emits `data/processed/features.parquet`.

## Milestone 3 — Signal model

- [ ] `research/models/lgbm.py` with config-driven training.
- [ ] `research/models/registry.py` writing `manifest.json` per run.
- [ ] Walk-forward CV with embargo in `research/cv.py`.
- [ ] One trained baseline model committed via registry (artifact path only).

## Milestone 4 — Strategy engine

- [ ] `strategies/base.py` abstract base class with `generate_orders(state)`.
- [ ] `strategies/examples/momentum_xover.py` baseline using the LGBM signal.
- [ ] `strategies/composer.py` for multi-signal blending (placeholder ok).

## Milestone 5 — Risk engine

- [ ] `risk/engine.py`: gross exposure, per-symbol cap, max leverage, daily loss.
- [ ] `risk/sizing.py`: volatility-targeted sizing.
- [ ] `risk/limits.py`: pydantic config loader from `configs/risk.yaml`.
- [ ] Unit tests for accept and reject paths on every check.

## Milestone 6 — Backtesting

- [ ] `backtests/engine.py` wrapping `vectorbt` with the project cost model.
- [ ] `backtests/run.py` CLI emitting the standard artifact set.
- [ ] `backtests/metrics.py`: Sharpe, Sortino, max DD, hit rate, turnover, PSR.
- [ ] Determinism test: same config → identical `metrics.json`.

## Milestone 7 — Execution

- [ ] `execution/brokers/base.py` abstract Broker interface.
- [ ] `execution/brokers/paper.py` using current bar fills + cost model.
- [ ] `execution/brokers/binance.py` REST + websocket adapter (testnet first).
- [ ] `execution/brokers/coinbase.py` adapter (sandbox first).
- [ ] `execution/runner.py` orchestrator wiring strategy → risk → broker.

## Milestone 8 — Monitoring

- [ ] `monitoring/logger.py` structlog setup with JSON output.
- [ ] `monitoring/metrics.py` PnL, exposure, drawdown gauges.
- [ ] `monitoring/drift.py` live-vs-backtest drift detector + alert hook.
- [ ] Kill-switch wiring: monitoring → risk → execution.

## Milestone 9 — Research artifacts

- [ ] `SIGNALS.md` populated with at least 3 starter hypotheses.
- [ ] `DECISIONS.md` records the chosen baseline model and risk limits.
- [ ] `docs/STRATEGY.md` documents the baseline strategy and target metrics.

---

## Milestone 10 — Backend API + Frontend

- [ ] `backend/api/app.py` FastAPI app with `/api/{trades,strategies,signals,backtests,system}`.
- [ ] `frontend/` Next.js + TypeScript dashboard with the seven required pages.
- [ ] `tests/e2e/test_api_app.py` exercises every router via `TestClient`.
- [ ] Frontend build runs in CI and the standalone Next image boots.

## Milestone 11 — Containers + CI

- [ ] `Dockerfile`, `backend/Dockerfile`, `frontend/Dockerfile` build cleanly.
- [ ] `docker-compose.yml` ties frontend, backend, engine, redis, duckdb to
      the existing `trading-net` (with `ollama` and `hermes` joined externally).
- [ ] `.github/workflows/ci.yml` runs lint, mypy, pytest (unit + e2e),
      backtest smoke, ai-eval, frontend build, docker builds, and gitleaks.

## Milestone 12 — AI evals

- [ ] `ai_evals/promptfoo/promptfooconfig.yaml` exercises every prompt
      with offline fixtures and (optionally) a live Ollama provider.
- [ ] `ai_evals/deepeval/test_*.py` enforces JSON shape and forbidden
      phrases (e.g. "deploy live"); runs offline in CI.

## Stretch (next sprint)

- Order book / trade-tape ingestion.
- LSTM and transformer baselines in `research/models/torch_*.py`.
- Multi-asset strategy composition.
- Portfolio-level risk parity in `risk/portfolio.py`.
- Live alerting via Slack / Telegram from `monitoring/alerts.py`.
- Live equity-curve and trade tape over websockets in the frontend.
- Replace `OFFLINE_LLM=true` shortcut with recorded Ollama responses
  generated by a nightly job.
