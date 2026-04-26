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

- [~] Implement `/styleguide`, component registry, local mock fixtures, and
  component tests from FEATURE-0034. **Paused-agent WIP** — see "Agent
  Coordination / Conflict Status" below. The work-in-progress file set lives
  on local branch `backup/chore-gov-pre-slim` (commit `07d05ab`) and is
  also present as untracked files in the working tree.
- [ ] Run full global gates locally (`pytest -q`, `ruff check .`,
  `mypy --strict .`, frontend lint/typecheck/build, e2e, backtest smoke)
  after the styleguide WIP lands. CI on `main` validates the same gates per
  push, so this is a local-tree check only.
- [ ] Decide whether to land the second commit on
  `backup/chore-gov-pre-slim` (`9913a86 feat(dev): one-shot frontend-init
  service for trading-node-modules`) — small dev-only quality-of-life that
  was sliced out of PR #3. Either cherry-pick into a tiny PR or drop the
  branch.

## Agent Coordination / Conflict Status

### Current Status

This repository was actively edited by **two parallel agent sessions** during
the 2026-04-26 work day:

1. **This session (Developer / audit)** — landed PR #3 (governance) and
   PR #17 (docker fix), reviewed the open Dependabot PR set, and ran this
   audit. Working strictly through `main`-derived branches; never touched
   the styleguide files. **FEATURE-0045** (Neko identity) was implemented
   additively on the same principle — no edits under paused-agent WIP paths.
2. **A paused agent** — was implementing FEATURE-0034 (`/styleguide`,
   component registry, vitest, operator components, charts, design tokens).
   Its WIP was committed to a chore branch as `07d05ab` and a parallel
   stash, both of which are now consolidated on `backup/chore-gov-pre-slim`.

The paused agent's WIP is currently visible as **untracked files in the
working tree** (under `frontend/components/`, `frontend/styleguide/`,
`frontend/styles/`, plus `frontend/vitest.{config,setup}.ts`). These files
are not lost; they exist both in the local working tree and as commit
`07d05ab` on `backup/chore-gov-pre-slim`. Either resume the paused agent or
have a human cherry-pick `07d05ab` into a `feat(frontend): styleguide` PR
when ready.

### Known Conflicts

- **Working-tree files vs `backup/chore-gov-pre-slim`** — the two are
  near-identical for the styleguide files; the branch tip is the canonical
  copy.
- **`backup/chore-gov-pre-slim` is local-only** — it does not exist on the
  remote; deleting the branch without first pushing or cherry-picking will
  permanently lose `9913a86` and `07d05ab`.
- **No deeper merge conflicts** with `main` are expected: the styleguide
  paths (`frontend/components/operator/`, `frontend/styleguide/`,
  `frontend/styles/tokens.css`, `frontend/components/charts/freshness-*`,
  `frontend/components/data/{evidence,metric,risk-limit,run-status}-*`,
  `frontend/components/ui/{button,empty-state,error-state,select,skeleton,
  textarea}.tsx`, `frontend/vitest.{config,setup}.ts`) are all new files
  that `main` does not touch.

### Remaining Work

- [!] **Resolve paused-agent WIP** (decision blocker, human only): resume
  the paused agent or cherry-pick `07d05ab` into a small PR.
- [ ] **Triage open Dependabot PRs** — see reviews already posted on PR #9
  (postcss), PR #13 (next 16; needs coupled React 19 bump), PR #16 (vite/
  vitest 4; lockfile-regen needed). PR #15 closed as duplicate of PR #16.
- [!] **Postcss alert #7** stays open until either a
  `package.json` `overrides.postcss = "^8.5.10"` lands or `next` ships a
  newer bundled postcss; PR #9 alone does not move it.
- [ ] **Drop local-only refs** `pr-13`, `pr-15`, `pr-16` (this audit will
  do it).

### Handoff Instructions for Future Agents

1. **Start here.** This `TODO.md` is the canonical continuation point.
   Read this section, then the latest entry in `SESSION_LOG.md`.
2. **Do not pop `stash@{0}` if it still exists.** Its content is already
   on `backup/chore-gov-pre-slim`; popping it would only re-create an
   untracked-file mess.
3. **Do not delete `backup/chore-gov-pre-slim`** until the styleguide WIP
   is landed in a PR, retired, or explicitly approved for deletion by the
   project owner. It is the only place `9913a86` exists.
4. **Spec source of truth** is `specs/trading-lab-platform/`. Use the
   `tasks.md` Wave 1 list for the next implementation focus; FEATURE-0034
   is the active operator-experience ticket.
5. **Risk path is non-bypassable** — see `DECISIONS.md` DEC-002, the
   `risk-management.mdc` rule, and `risk/engine.py`. Do not add a
   `skip_risk` flag, even for tests.
6. **CI is green on `main`** as of `8174b0b`. New PRs should expect all six
   required checks (`Analyze`, `lint · ruff`, `types · mypy --strict`,
   `test · unit + strategy + cursor harness`, `test · security suite`,
   `security · gitleaks`) plus the now-green `docker · build images` to
   pass. Solo-owner CODEOWNERS still blocks self-merge; use
   `gh pr merge <n> --admin --squash --delete-branch` for owner PRs.

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
