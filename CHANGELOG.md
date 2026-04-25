# Changelog

## 0.3.1 — 2026-04-25

### Added

- No-key public ingesters: `BinancePublicIngester`, `CoinbasePublicIngester`, `YFinanceIngester` (`Exchange.YAHOO`); `data/ingest.run` `--source` flag; optional `public-data` extra (`yfinance`).
- `runs/events`: `InMemoryEventBus`, `RedisEventBus`, `get_event_bus()`; `GET /api/system/health` includes `redis_disabled` when Redis is intentionally off.
- `docs/REMINDERS.md`, `RUNNING.md` ingest examples; spec addendum FEATURE-0041–0043 in `specs/trading-lab-platform/`.

### Changed

- `test_no_secrets` only fails on **git-tracked** `.env` / `.env.local` (local untracked `.env` allowed).

## 0.3.0 — 2026-04-25

### Added

- Canonical JSON (`monitoring.canonical_json`) and deterministic `metrics.json` / `manifest.json` writers.
- Hash-chained audit tables (`ha_*`) and `python -m monitoring.audit verify --tables critical`.
- `runs/` package: frozen `RunConfig`, `RunOrchestrator`, boot recovery, isolation contextvars, DuckDB outbox.
- `learning/` OOS-only `RunSummary` + four lever scorers + `scoreboard` table.
- `GET /api/runs`, extended `GET /api/system/health` (`audit_chain_ok`), `POST /api/system/kill-switch/*`, `GET /metrics` (Prometheus when installed).
- Frontend routes: `/runs`, `/runs/[runId]`, `/runs/compare`, `/learnings`, `/login`, `/styleguide`, `/configuration/*` (kitsune palette).
- Security tests: risk path import scan, no bypass tokens in app code, `runs/` LLM isolation, outbox idempotency.

### Changed

- CI split into lint, typecheck, unit, det, security, e2e, backtest smoke, frontend, gitleaks, docker jobs.
- `Backtest` synthetic bars use fixed time anchor for reproducible smoke/det tests.
- `RiskEngine` emits `RiskDecision` records when a `RiskAudit` sink is attached.

## 0.2.0 — 2026-04-25

### Added

- `execution.brokers.registry.LiveBrokerRegistry` (MVP-0 default lock) unless `configs/runtime.yaml` unlocks live adapters.
- `tests/security/test_live_registration_forbidden.py`.
- `configs/runtime.yaml` with `live_adapters_unlocked: false`.

### Changed

- `execution/runner.py` routes broker selection through the registry; locked live brokers fail with a clear CLI error.
- `BinanceLive` / `CoinbaseLive` aliases for design parity.

## Unreleased
