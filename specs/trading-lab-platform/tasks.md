# Trading Lab Platform Tasks

## Purpose

This file indexes the epic and feature task structure derived from requirements.md and design.md for the trading-lab-platform spec. Detailed work is split into product/spec tickets under tasks/, where each epic explains the broader capability and each feature ticket explains why and what must be built without over-prescribing implementation details.

## Source Documents

- requirements.md
- design.md
- specs/README.md
- .cursor/rules/spec-sessions.mdc
- .cursor/rules/architecture.mdc
- .cursor/rules/security.mdc
- .cursor/rules/workflow.mdc
- .cursor/rules/ai-workflow.mdc
- AGENTS.md
- PROJECT_CONTEXT.md
- TODO.md
- DECISIONS.md
- SESSION_LOG.md

## Assumptions

- The requested .kiro/specs/trading-lab-platform/ tree is represented in this repo by specs/trading-lab-platform/; no committed .kiro/ directory exists.
- This task system uses tasks/ epic and feature ticket files because the user explicitly requested a ticket system rather than the older single-checklist template.
- MVP-0 is treated as the first production milestone; v1, v1.x, v1.1, and v2.x work remains traceable but sequenced after MVP-0.
- Feature tickets describe why and what. Implementation agents must still read requirements.md and design.md before coding.

## Execution Principles

- Tickets explain why and what, not detailed how.
- Features should be implementation-ready but not implementation-prescriptive.
- Work should follow repo standards, Cursor spec-session rules, and the trading-lab architecture/security rules.
- Each feature should be independently reviewable.
- Each feature should include validation expectations.
- Each feature should preserve traceability back to requirements and design.
- Implementation agents must preserve the immutable pipeline order and non-bypassable risk path.
- LLM features remain research/operator-assistance capabilities and never enter the execution path.

## Epic Roadmap

| Order | Epic | Purpose | Status | Path |
|---:|---|---|---|---|
| 1 | Platform Foundation and Governance | Keep the platform buildable, auditable, and aligned with MVP-0 invariants before product surfaces expand. | Proposed | tasks/platform-foundation-governance/epic.md |
| 2 | Market Data and Intelligence Ingestion | Give runs trustworthy market, portfolio, and external intelligence inputs with freshness and provenance controls. | Proposed | tasks/market-data-intelligence/epic.md |
| 3 | Run Engine and Memory | Make each experiment a reproducible, isolated run with durable artifacts, event history, and bounded autonomy. | Proposed | tasks/run-engine-memory/epic.md |
| 4 | Research Datasets, Features, and Models | Convert raw data into point-in-time datasets, registered features, labels, and calibrated model artifacts. | Proposed | tasks/research-datasets-models/epic.md |
| 5 | Strategy Framework and Learning Loop | Let the platform test, rank, promote, demote, and learn from strategies without exceeding evidence or risk boundaries. | Proposed | tasks/strategy-learning/epic.md |
| 6 | Backtesting and Simulation | Produce honest, deterministic simulations that justify or falsify strategy changes before paper or live exposure. | Proposed | tasks/backtesting-simulation/epic.md |
| 7 | Risk and Execution Safety | Protect capital by keeping all target positions behind risk checks, broker registry, paper simulation, reconciliation, and live gates. | Proposed | tasks/risk-execution-safety/epic.md |
| 8 | LLM and AI Assistance | Use LLMs for research, summaries, calibration, and operator assistance while keeping them out of the trading path. | Proposed | tasks/llm-ai-assistance/epic.md |
| 9 | Backend API and Streaming | Expose run, strategy, configuration, audit, and command capabilities through typed APIs and realtime event streams. | Proposed | tasks/backend-api-streaming/epic.md |
| 10 | Frontend Operator Experience | Give a single operator a beginner-safe dashboard for runs, strategy evidence, configuration, learning, alerts, and diagnostics. | Proposed | tasks/frontend-operator-experience/epic.md |
| 11 | Observability, Audit, and Operations | Make the platform diagnosable, explainable, and recoverable through logs, alerts, audit trails, retention, and runbooks. | Proposed | tasks/observability-audit-operations/epic.md |
| 12 | Deployment, Security, and CI | Package and validate the platform for self-hosted Unraid operation with secure secrets, containers, CI gates, and recovery paths. | Proposed | tasks/deployment-security-ci/epic.md |

## Feature Index

| ID | Feature | Epic | Status | Path |
|---|---|---|---|---|
| FEATURE-0001 | MVP-0 Release Invariants and Readiness Gate | Platform Foundation and Governance | Proposed | tasks/platform-foundation-governance/mvp0_release_invariants_0001.md |
| FEATURE-0002 | Architecture Decision and System State Records | Platform Foundation and Governance | Proposed | tasks/platform-foundation-governance/architecture_decision_system_state_0002.md |
| FEATURE-0003 | Contribution Workflow and Cursor Harness Governance | Platform Foundation and Governance | Proposed | tasks/platform-foundation-governance/contribution_cursor_harness_0003.md |
| FEATURE-0004 | Market Source Catalog and Symbol Policy | Market Data and Intelligence Ingestion | Proposed | tasks/market-data-intelligence/market_source_catalog_0004.md |
| FEATURE-0005 | Historical and Realtime Ingestion Freshness | Market Data and Intelligence Ingestion | Proposed | tasks/market-data-intelligence/historical_realtime_freshness_0005.md |
| FEATURE-0006 | Manual Insight Intake and Source Confirmation | Market Data and Intelligence Ingestion | Proposed | tasks/market-data-intelligence/manual_insight_confirmation_0006.md |
| FEATURE-0007 | Schwab CSV Portfolio Context | Market Data and Intelligence Ingestion | Proposed | tasks/market-data-intelligence/schwab_csv_portfolio_context_0007.md |
| FEATURE-0008 | Run Lifecycle and Isolation | Run Engine and Memory | Proposed | tasks/run-engine-memory/run_lifecycle_isolation_0008.md |
| FEATURE-0009 | Run Memory and Artifact Replay | Run Engine and Memory | Proposed | tasks/run-engine-memory/run_memory_artifact_replay_0009.md |
| FEATURE-0010 | MVP-0 and v1 Run Type Catalog | Run Engine and Memory | Proposed | tasks/run-engine-memory/run_type_catalog_0010.md |
| FEATURE-0011 | Approval Queue and Autonomy Boundaries | Run Engine and Memory | Proposed | tasks/run-engine-memory/approval_autonomy_boundaries_0011.md |
| FEATURE-0012 | Dataset Snapshots and Replay Contracts | Research Datasets, Features, and Models | Proposed | tasks/research-datasets-models/dataset_snapshots_replay_0012.md |
| FEATURE-0013 | Point-in-Time Feature Registry | Research Datasets, Features, and Models | Proposed | tasks/research-datasets-models/point_in_time_feature_registry_0013.md |
| FEATURE-0014 | Model Training, Evaluation, and Registry | Research Datasets, Features, and Models | Proposed | tasks/research-datasets-models/model_training_registry_0014.md |
| FEATURE-0015 | Strategy Library and Evidence Ladder | Strategy Framework and Learning Loop | Proposed | tasks/strategy-learning/strategy_library_evidence_ladder_0015.md |
| FEATURE-0016 | Adaptive Universe and Bandit Allocation | Strategy Framework and Learning Loop | Proposed | tasks/strategy-learning/adaptive_universe_bandit_0016.md |
| FEATURE-0017 | OOS-Only Learning Lever Scoring | Strategy Framework and Learning Loop | Proposed | tasks/strategy-learning/oos_learning_lever_scoring_0017.md |
| FEATURE-0018 | Deterministic Backtest Artifacts | Backtesting and Simulation | Proposed | tasks/backtesting-simulation/deterministic_backtest_artifacts_0018.md |
| FEATURE-0019 | Realistic Cost, Slippage, and Liquidity Modeling | Backtesting and Simulation | Proposed | tasks/backtesting-simulation/realistic_cost_slippage_0019.md |
| FEATURE-0020 | Backtest Comparison and Gap Analysis | Backtesting and Simulation | Proposed | tasks/backtesting-simulation/backtest_comparison_gap_analysis_0020.md |
| FEATURE-0021 | Non-Bypassable Risk Path | Risk and Execution Safety | Proposed | tasks/risk-execution-safety/non_bypassable_risk_path_0021.md |
| FEATURE-0022 | Paper Broker and Broker Registry | Risk and Execution Safety | Proposed | tasks/risk-execution-safety/paper_broker_registry_0022.md |
| FEATURE-0023 | Fill Reconciliation and Account State | Risk and Execution Safety | Proposed | tasks/risk-execution-safety/fill_reconciliation_account_state_0023.md |
| FEATURE-0024 | Live Enablement Gate and Manual Override Ceremony | Risk and Execution Safety | Proposed | tasks/risk-execution-safety/live_enablement_gate_0024.md |
| FEATURE-0025 | Ollama Provider and LLM Trace Logging | LLM and AI Assistance | Proposed | tasks/llm-ai-assistance/ollama_provider_trace_logging_0025.md |
| FEATURE-0026 | Task-Type Calibration as a Research Signal | LLM and AI Assistance | Proposed | tasks/llm-ai-assistance/task_type_calibration_0026.md |
| FEATURE-0027 | Dashboard Chat Command Bus | LLM and AI Assistance | Proposed | tasks/llm-ai-assistance/dashboard_chat_command_bus_0027.md |
| FEATURE-0028 | Run, Strategy, and Config API Surfaces | Backend API and Streaming | Proposed | tasks/backend-api-streaming/run_strategy_config_api_0028.md |
| FEATURE-0029 | Asynchronous Mutating Command Pattern | Backend API and Streaming | Proposed | tasks/backend-api-streaming/async_mutating_command_pattern_0029.md |
| FEATURE-0030 | Realtime Run Event Streaming | Backend API and Streaming | Proposed | tasks/backend-api-streaming/realtime_run_event_streaming_0030.md |
| FEATURE-0031 | Dashboard Information Architecture and Run UX | Frontend Operator Experience | Proposed | tasks/frontend-operator-experience/dashboard_information_architecture_0031.md |
| FEATURE-0032 | Configuration and Risk Controls UX | Frontend Operator Experience | Proposed | tasks/frontend-operator-experience/configuration_risk_controls_ux_0032.md |
| FEATURE-0033 | Learning, Backtest, and Strategy Comparison UX | Frontend Operator Experience | Proposed | tasks/frontend-operator-experience/learning_backtest_comparison_ux_0033.md |
| FEATURE-0034 | Style Guide and Component Library | Frontend Operator Experience | Proposed | tasks/frontend-operator-experience/style_guide_component_library_0034.md |
| FEATURE-0045 | Neko Quant brand identity (additive) | Frontend Operator Experience | Landed 2026-04-26 | tasks/frontend-operator-experience/neko_quant_identity_0045.md |
| FEATURE-0046 | Neko animated mascot | Frontend Operator Experience | Proposed | tasks/frontend-operator-experience/neko_animated_mascot_0046.md |
| FEATURE-0047 | Neko sound design | Frontend Operator Experience | Proposed | tasks/frontend-operator-experience/neko_sound_design_0047.md |
| FEATURE-0048 | Neko hacker mode terminal | Frontend Operator Experience | Proposed | tasks/frontend-operator-experience/neko_hacker_mode_0048.md |
| FEATURE-0049 | Neko achievement badges (persistence) | Frontend Operator Experience | Proposed | tasks/frontend-operator-experience/neko_achievements_0049.md |
| FEATURE-0035 | Structured Logs, Metrics, and SLOs | Observability, Audit, and Operations | Proposed | tasks/observability-audit-operations/structured_logs_metrics_slos_0035.md |
| FEATURE-0036 | Notifications and Seven Operational Alerts | Observability, Audit, and Operations | Proposed | tasks/observability-audit-operations/notifications_seven_alerts_0036.md |
| FEATURE-0037 | Hash-Chained Audit and Decision Explainability | Observability, Audit, and Operations | Proposed | tasks/observability-audit-operations/hash_chained_audit_explainability_0037.md |
| FEATURE-0038 | Docker and Unraid Deployment Topology | Deployment, Security, and CI | Proposed | tasks/deployment-security-ci/docker_unraid_topology_0038.md |
| FEATURE-0039 | CI/CD and Quality Gates | Deployment, Security, and CI | Proposed | tasks/deployment-security-ci/cicd_quality_gates_0039.md |
| FEATURE-0040 | Secrets and Security Controls | Deployment, Security, and CI | Proposed | tasks/deployment-security-ci/secrets_security_controls_0040.md |
| FEATURE-0041 | No-Key Public Ingestion and Source CLI | Market Data and Intelligence Ingestion | **Implemented** (addendum 2026-04-25) | See addendum in requirements/design; code: `data/ingest/binance_public.py`, `coinbase_public.py`, `yfinance_source.py`, `data/ingest/run.py`, `data/types.py`, `tests/data/` |
| FEATURE-0042 | Optional Redis, In-Memory Event Bus, Health Semantics | Run Engine and Memory; Backend API and Streaming; Deployment | **Implemented** (addendum 2026-04-25) | See addendum; code: `runs/events/in_memory.py`, `redis_bus.py`, `factory.py`, `backend/api/routers/system.py`, `tests/runs/`, `tests/e2e/test_health_redis_optional.py` |
| FEATURE-0043 | Operator env clarity (Reminders, .env.example, RUNNING) | Platform Foundation and Governance | **Implemented** (addendum 2026-04-25) | `docs/REMINDERS.md`, `.env.example`, `RUNNING.md` |

## Addendum: MVP-0 run UI/API and dev-speed Docker audit (2026-04-26)

This addendum audits the current session's work against the platform task
system. It is intentionally evidence-based and does not mark broad feature
tickets fully complete unless the feature's validation expectations are met.

| Area | Status | Evidence | Spec mapping | Remaining gap |
|---|---|---|---|---|
| Shared Docker base and dev loop | partial | `Dockerfile.base`, `Dockerfile`, `backend/Dockerfile`, `Dockerfile.research`, `docker-compose.dev.yml`, `dev.py`; `docker build -f Dockerfile.base -t trading-base .` cached rebuild in 2.8s | FEATURE-0038, Req 37/39/40 | Production compose now depends on a locally built `trading-base` image; CI should either build/tag it first or add a compose `base` target/registry cache. |
| Windows Docker Desktop bind-mount performance | done for dev override | Anonymous-volume overlays in `docker-compose.dev.yml` mask `.venv`, `.git`, caches, and `frontend/node_modules`; `/app` visible size dropped from ~3GB to 5.7MB; unit suite dropped from 928s/incomplete to 53s passing | FEATURE-0038, FEATURE-0039 | Document this as a required Windows dev pattern and keep it in Docker rules. |
| Run list/detail/compare UI | partial | `frontend/app/runs/page.tsx`, `frontend/app/runs/[runId]/page.tsx`, `frontend/app/runs/compare/page.tsx`, `frontend/lib/api.ts`; `291 passed, 1 deselected` in dev container | FEATURE-0031, FEATURE-0033, Req 33/35/44 | Pages are wired but not component-first/styleguide-backed yet; frontend lint/typecheck/build still need to be run after styleguide rules land. |
| Learning scoreboard UI/API | partial | `backend/api/routers/learnings.py`, `frontend/app/learnings/page.tsx`, `learning/scorers/standard.py` | FEATURE-0017, FEATURE-0033, Req 44 | LLM calibration remains an OOS hit-rate proxy with weight 0.0 until v1 task-type calibration ships. |
| Run worker and recovery path | partial | `runs/worker.py`, `runs/orchestrator.py`, `backend/api/app.py`, `execution/runner.py`, tests under `tests/runs/` and `tests/e2e/` | FEATURE-0008, FEATURE-0009, FEATURE-0018, FEATURE-0028 | Worker uses synthetic MVP-0 bars by default; real market-data integration remains Wave 2. |
| Run isolation guard | partial | `runs/isolation.py`, checks added in audit/scorer write paths, `tests/runs/test_isolation.py` | FEATURE-0008, Day-0 Invariant 5 | More writer paths should be audited before this is marked complete. |
| Durable event publish facade | partial | `runs/events/bus.py`, `backend/api/routers/sse.py`, `tests/security/test_direct_redis_use.py` | FEATURE-0030, FEATURE-0037 | SSE is DuckDB-durable replay only; Redis Streams blocking fan-out remains v1. |
| Styleguide source of truth | strengthened, not implemented | `tasks/frontend-operator-experience/style_guide_component_library_0034.md`, `.cursor/rules/component-first.mdc` planned in this addendum | FEATURE-0034, Req 50 | `/styleguide`, component registry, demo fixtures, and component tests still need implementation. |
| Cursor workflow reliability | partial | `.cursor/hooks/README.md` stale match semantics identified; context routing/rules to be updated in this session | FEATURE-0003, Req 49/51 | Hooks and skills are fail-open/advisory; harness tests must be run after routing/doc updates. |

**Verification captured in session:**

- `docker compose -f docker-compose.yml -f docker-compose.dev.yml build` → success after base image build.
- `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d` → services start.
- `Invoke-WebRequest http://localhost:8000/api/system/health` → 200 with `{"status":"ok", ...}`.
- Backend hot reload verified: `WatchFiles detected changes in 'backend/api/routers/runs.py'. Reloading...`.
- `pytest -q -m "not slow and not integration"` inside backend dev container → `291 passed, 1 deselected, 3 warnings in 53.24s`.
- Research container imports → `torch=2.11.0+cu130`, `lightgbm=4.6.0`, `vectorbt=1.0.0`, `xgboost=3.2.0`.
- `docker compose ... down` then `up -d` with volumes preserved → 24.7s.
- `ruff check dev.py` → all checks passed.
- `mypy --strict --explicit-package-bases dev.py` → success.

## Addendum: OpenAPI Swagger UI themed to operator console (2026-04-26)

- **Scope:** FastAPI `/docs` serves Swagger UI with a vendored dark stylesheet
  that mirrors the cyberpunk operator palette in
  `frontend/tailwind.config.ts` (see FEATURE-0034 design direction).
- **Code:** [`backend/api/static/swagger-trading-lab.css`](../backend/api/static/swagger-trading-lab.css),
  [`backend/api/app.py`](../backend/api/app.py) (`docs_url=None`, `StaticFiles` on `/static`,
  `get_swagger_ui_html` + `syntaxHighlight.theme: obsidian`).
- **Tests:** [`tests/e2e/test_api_app.py`](../tests/e2e/test_api_app.py) (`test_swagger_docs_serves_themed_html`,
  `test_swagger_theme_css_is_served`).
- **Note:** ReDoc at `/redoc` is unchanged (default light theme) until a
  dedicated task themes it. Full `/styleguide` route remains FEATURE-0034
  scope.

## Addendum: No-key MVP slice (2026-04-25)

**Scope (aligned with `simple-no-key-mvp` implementation plan):**

- [x] **Public ingesters** — Binance and Coinbase REST without keys; yfinance
  for Yahoo; `Exchange.YAHOO`; `--source` on ingest CLI; optional
  `public-data` extra in `pyproject.toml`.
- [x] **Redis optional** — `redis_disabled` + `redis_ok` on health when
  `REDIS_URL` empty; in-memory + Redis bus behind `get_event_bus()`.
- [x] **Docs** — Backend vs frontend env table; Hermes unused for MVP-0; Redis
  in Docker vs omitted locally; DuckDB vs SQLite note.

**_Requirements: Addendum A, B, C, D (requirements.md)._**

**Verification (definition of done for this addendum):** `ruff check .`, `mypy
--strict --explicit-package-bases .`, `pytest -q`, `pytest -q -m e2e`, `python -m
backtests.smoke`, `python -m monitoring.audit verify --tables critical` (ingest
live runs may be geo/network dependent; unit tests mock HTTP).

## Suggested Execution Order

### Wave 1 - MVP-0 Safety Foundation

- [ ] FEATURE-0001 - MVP-0 Release Invariants and Readiness Gate
- [ ] FEATURE-0002 - Architecture Decision and System State Records
- [ ] FEATURE-0003 - Contribution Workflow and Cursor Harness Governance
- [ ] FEATURE-0021 - Non-Bypassable Risk Path
- [ ] FEATURE-0022 - Paper Broker and Broker Registry
- [ ] FEATURE-0037 - Hash-Chained Audit and Decision Explainability
- [ ] FEATURE-0039 - CI/CD and Quality Gates
- [ ] FEATURE-0040 - Secrets and Security Controls

### Wave 2 - Core Run and Data Loop

- [ ] FEATURE-0004 - Market Source Catalog and Symbol Policy
- [ ] FEATURE-0005 - Historical and Realtime Ingestion Freshness
- [ ] FEATURE-0008 - Run Lifecycle and Isolation
- [ ] FEATURE-0009 - Run Memory and Artifact Replay
- [ ] FEATURE-0010 - MVP-0 and v1 Run Type Catalog
- [ ] FEATURE-0012 - Dataset Snapshots and Replay Contracts
- [ ] FEATURE-0013 - Point-in-Time Feature Registry
- [ ] FEATURE-0018 - Deterministic Backtest Artifacts
- [ ] FEATURE-0019 - Realistic Cost, Slippage, and Liquidity Modeling

### Wave 3 - Research, Strategy, and Learning

- [ ] FEATURE-0014 - Model Training, Evaluation, and Registry
- [ ] FEATURE-0015 - Strategy Library and Evidence Ladder
- [ ] FEATURE-0016 - Adaptive Universe and Bandit Allocation
- [ ] FEATURE-0017 - OOS-Only Learning Lever Scoring
- [ ] FEATURE-0020 - Backtest Comparison and Gap Analysis
- [ ] FEATURE-0025 - Ollama Provider and LLM Trace Logging
- [ ] FEATURE-0026 - Task-Type Calibration as a Research Signal

### Wave 4 - Operator Product Surface

- [ ] FEATURE-0028 - Run, Strategy, and Config API Surfaces
- [ ] FEATURE-0029 - Asynchronous Mutating Command Pattern
- [ ] FEATURE-0030 - Realtime Run Event Streaming
- [ ] FEATURE-0031 - Dashboard Information Architecture and Run UX
- [ ] FEATURE-0032 - Configuration and Risk Controls UX
- [ ] FEATURE-0033 - Learning, Backtest, and Strategy Comparison UX
- [ ] FEATURE-0034 - Style Guide and Component Library
- [ ] FEATURE-0027 - Dashboard Chat Command Bus

### Wave 5 - Production Readiness and v1 Expansion

- [ ] FEATURE-0006 - Manual Insight Intake and Source Confirmation
- [ ] FEATURE-0007 - Schwab CSV Portfolio Context
- [ ] FEATURE-0011 - Approval Queue and Autonomy Boundaries
- [ ] FEATURE-0023 - Fill Reconciliation and Account State
- [ ] FEATURE-0024 - Live Enablement Gate and Manual Override Ceremony
- [ ] FEATURE-0035 - Structured Logs, Metrics, and SLOs
- [ ] FEATURE-0036 - Notifications and Seven Operational Alerts
- [ ] FEATURE-0038 - Docker and Unraid Deployment Topology

## Traceability Matrix

| Requirement / Design Area | Epic | Feature Tickets |
|---|---|---|
| Req 1-2, MVP-0 acceptance, capital phases | Platform Foundation and Governance; Backtesting and Simulation | FEATURE-0001, FEATURE-0018, FEATURE-0020 |
| Req 3, 19, 30 market scope, ingestion, freshness | Market Data and Intelligence Ingestion | FEATURE-0004, FEATURE-0005 |
| Req 5 Schwab read-only path | Market Data and Intelligence Ingestion | FEATURE-0007 |
| Req 6-12 run engine, memory, run types, artifacts | Run Engine and Memory | FEATURE-0008, FEATURE-0009, FEATURE-0010, FEATURE-0011 |
| Req 13-15, 27 strategy evidence and universe | Strategy Framework and Learning Loop | FEATURE-0015, FEATURE-0016 |
| Req 16, 22, 23 LLM stack and isolation | LLM and AI Assistance; Research Datasets, Features, and Models | FEATURE-0014, FEATURE-0025, FEATURE-0026, FEATURE-0027 |
| Req 17, 44-45 learning and auto-apply | Strategy Framework and Learning Loop; Run Engine and Memory | FEATURE-0011, FEATURE-0017 |
| Req 18, 9 manual insight and source confirmation | Market Data and Intelligence Ingestion | FEATURE-0006 |
| Req 20, 24-25 risk path, limits, trust model | Risk and Execution Safety | FEATURE-0021, FEATURE-0022, FEATURE-0023, FEATURE-0024 |
| Req 26, 28-29 reproducibility, datasets, features | Research Datasets, Features, and Models; Backtesting and Simulation | FEATURE-0012, FEATURE-0013, FEATURE-0018 |
| Req 31-32 notifications and alerts | Observability, Audit, and Operations; Risk and Execution Safety | FEATURE-0024, FEATURE-0036 |
| Req 33-35 UI, config, realtime | Backend API and Streaming; Frontend Operator Experience | FEATURE-0028, FEATURE-0029, FEATURE-0030, FEATURE-0031, FEATURE-0032 |
| Req 36, 41-42 explainability, logs, state | Observability, Audit, and Operations; Backend API and Streaming | FEATURE-0035, FEATURE-0037 |
| Req 37-40 hosting, backup, free tooling, CI | Deployment, Security, and CI | FEATURE-0038, FEATURE-0039, FEATURE-0040 |
| Req 43 out-of-scope boundaries | Platform Foundation and Governance; Risk and Execution Safety | FEATURE-0001, FEATURE-0022, FEATURE-0024 |
| Req 46-51 engineering quality, libraries, web research, Cursor, style guide | Platform Foundation and Governance; Frontend Operator Experience; Deployment, Security, and CI | FEATURE-0002, FEATURE-0003, FEATURE-0034, FEATURE-0039 |
| Addendum A–D (2026-04-25) no-key ingest, optional Redis, env docs | Market Data; Run Engine; Backend; Platform Foundation | FEATURE-0041, FEATURE-0042, FEATURE-0043 |

## Open Questions

- (Resolved 2026-04-26) **Repository visibility:** the GitHub remote is **public**;
  fork PR and CI expectations are captured in `requirements.md` / `design.md`
  addenda (2026-04-26) and `docs/CONTRIBUTING.md`.
- Should the repo later mirror specs/ into .kiro/ for external Kiro tooling, or is specs/ the permanent canonical location?
- Which command should be canonical for the final backtest smoke gate: pytest tests/e2e -q plus python -m backtests.smoke, or only the workflow rule variant?
- Should v1.x Schwab OAuth and v1.1 live-broker enablement remain in this broad platform spec or split into smaller follow-up specs before implementation?

## Quality Checklist

- [x] All requirements are represented by at least one epic or feature.
- [x] All major design components are represented.
- [x] Each feature has acceptance criteria.
- [x] Each feature has validation expectations.
- [x] Each feature explains why and what.
- [x] No feature over-prescribes implementation details.
- [x] Tasks align with Cursor spec-session and workflow rules.
- [x] Tasks align with architecture, security, risk, and LLM rules.
- [x] File paths and links are valid within specs/trading-lab-platform/.

## Self-Review Notes

- requirements.md was analyzed for all 51 requirements and non-functional constraints.
- design.md was analyzed for MVP-0 sequencing, 23 components, domain/data models, API, testing, deployment, observability, and risk/security sections.
- The previous placeholder tasks.md was replaced because it contained template variables and did not represent the approved design.
- No .kiro/steering files were available in this repo; .cursor rules and specs/README.md are the active steering system.

---

## Addendum: Public GitHub repository — maintainer checklist (2026-04-26)

**Resolved:** The canonical GitHub remote for this project is **public**
(`finalFlick/market-prediction` at time of writing). The threat model includes
**fork PRs** and **workflow abuse**.

### Maintainer checklist (GitHub UI + repo config)

Re-verify after org moves, visibility changes, or new secrets:

- [ ] **Rulesets** (or branch protection) on `main`: required status checks from
      `ci`, `CodeQL`, and Pages where applicable; block force-push.
- [ ] **Actions → Workflow permissions**: default `GITHUB_TOKEN` read-only org-
      wide or per-repo; workflows elevate only scoped permissions (see
      `.github/workflows/ci.yml` `permissions` block).
- [ ] **Secret scanning** + **Push protection** enabled for the public repo.
- [ ] **Dependabot** security and version updates enabled (config:
      `.github/dependabot.yml`).
- [ ] **Code scanning** (CodeQL) enabled from `.github/workflows/codeql.yml`.
- [ ] **CODEOWNERS** accurate for `@finalFlick` or successor handles
      (`.github/CODEOWNERS`).
- [ ] **Fork PR audit:** no job running arbitrary code from `pull_request` forks
      uses repository secrets; avoid `pull_request_target` + untrusted checkout
      without a documented, reviewed exception.

### Feature mapping

| Area | Feature ticket |
|------|----------------|
| CI gates, least-privilege Actions, composite setup | FEATURE-0039 |
| Secrets, scanning, contributor security docs | FEATURE-0040 |
| Contribution loop, Cursor harness alignment | FEATURE-0003 |

### Spec documents updated with this addendum

- `requirements.md` — Addendum **Requirement E** (public repo CI and secrets).
- `design.md` — Addendum **Public GitHub repository — CI/CD trust zones**.
- `tasks.md` — this checklist.

### Traceability matrix row (additive)

| Requirement / Design Area | Epic | Feature Tickets |
|---|---|---|
| Addendum E (2026-04-26) public GitHub, fork CI, Dependabot, CodeQL | Deployment, Security, and CI; Platform Foundation | FEATURE-0039, FEATURE-0040, FEATURE-0003 |

---

## Addendum: PR #17 — `docker · build images` regression fix (2026-04-26)

**Scope:** Land the `trading-base` shared-Python-layers build step that
was sliced out of PR #3, fixing the `docker · build images` job that had
been failing on every PR since `4d7478e`. Merged at `8174b0b`.

| Item | Outcome |
|---|---|
| Inline `trading-base` build in CI `docker` job | Implemented (`.github/workflows/ci.yml`) |
| Dedicated publish workflow for GHCR `:cache` | Implemented (`.github/workflows/trading-base.yml`) |
| `build-contexts` redirect for `FROM trading-base` | Reverted in favor of `driver: docker` (BuildKit `build-contexts: docker-image://...` still resolves via registry, not local Docker) |
| `cache-from: type=registry` registry warming | Removed from CI; BuildKit aborts on both 403 (auth) and 404 (cache miss). `trading-base.yml` keeps `cache-to: type=registry` for external consumers |
| Buildx driver | Switched from default `docker-container` to `docker` driver so the host Docker daemon's image store is shared between the trading-base / engine / backend / frontend build steps. **Trade-off:** `docker` driver does not support `cache-from/to: type=gha`, so trading-base pays a cold pip-install (~3-5 min) on every PR run |
| Pre-existing Dockerfile bug | `frontend/Dockerfile` copies `/app/public`; `frontend/public/` did not exist in the repo. Fixed by adding `frontend/public/.gitkeep` |

**Code:** `.github/workflows/ci.yml`, `.github/workflows/trading-base.yml`,
`.cursor/rules/docker.mdc`, `frontend/public/.gitkeep`,
`specs/trading-lab-platform/tasks/deployment-security-ci/docker_unraid_topology_0038.md`.

**Feature mapping:** FEATURE-0038, FEATURE-0039.

**Follow-up:** once `trading-base.yml` runs on `main` and populates the
GHCR `:cache` ref, evaluate whether to reintroduce `cache-from:
type=registry` on the CI `docker` job (would require switching back to
`docker-container` driver and re-solving the local-image-resolution
problem). Tracked under FEATURE-0038 audit row.

---

## Addendum: Agent Coordination and Handoff (2026-04-26)

This addendum exists because the 2026-04-26 work day involved **two
parallel agent sessions** editing the repository concurrently. Future
agents must read this section before assuming `main` reflects every
in-flight change.

### Pattern observed

1. One session focused on **public-repo governance, CI hardening, and the
   docker · build images regression fix** (PRs #3 and #17). All work
   landed in `main`.
2. A second session focused on **FEATURE-0034 (`/styleguide`, component
   registry, vitest, design tokens, operator components, charts)**. That
   work was paused before any commit reached the remote. Its WIP is
   captured in two places only:
   - **Local branch `backup/chore-gov-pre-slim`** — sole holder of
     `9913a86` (frontend-init compose service) and `07d05ab` (full
     styleguide inventory). **Local-only**; deleting it loses both.
   - **Untracked files in the working tree** — same content as
     `07d05ab` for the styleguide files (under
     `frontend/components/{operator,charts,data,ui}/`,
     `frontend/styleguide/`, `frontend/styles/`, plus
     `frontend/vitest.{config,setup}.ts`).

### Handoff rules for future agents

- **Do not delete `backup/chore-gov-pre-slim`** without first
  cherry-picking its commits into a remote PR or getting explicit
  approval from the project owner. It is the only place
  `9913a86` and `07d05ab` exist.
- **Do not pop the `wip-all-before-slim-pr3` stash** if it still appears
  in `git stash list`. Its content is fully on
  `backup/chore-gov-pre-slim`; popping it just re-creates an
  untracked-file mess.
- **`TODO.md`** (root) is the canonical continuation point. Read its
  **Agent Coordination / Conflict Status** section first; pick a task
  from there or from the Wave 1 list above.
- **No file-level conflicts** are expected when the styleguide WIP is
  finally landed: every path it touches is a new file. The merge will be
  additive.

### What this addendum does NOT change

- No change to MVP-0 invariants, requirements, or design decisions.
- No change to risk-engine / LLM-isolation / look-ahead boundaries.
- No change to the ticket structure or epic ordering. FEATURE-0034
  remains the operator-experience styleguide ticket; the paused-agent WIP
  is a partial implementation of it, not a replacement.

### Open questions (not new, just consolidated for clarity)

- Should `9913a86` (frontend-init compose service) ship as its own tiny
  PR, or be retired? It is a developer-experience-only change and was
  superseded for CI by PR #17.
- Should we standardize a "`backup/<topic>` branches are local-only and
  ephemeral; nothing canonical lives there" convention so future
  parallel-agent stashes don't risk silent data loss?
