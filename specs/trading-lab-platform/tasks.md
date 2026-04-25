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
| FEATURE-0035 | Structured Logs, Metrics, and SLOs | Observability, Audit, and Operations | Proposed | tasks/observability-audit-operations/structured_logs_metrics_slos_0035.md |
| FEATURE-0036 | Notifications and Seven Operational Alerts | Observability, Audit, and Operations | Proposed | tasks/observability-audit-operations/notifications_seven_alerts_0036.md |
| FEATURE-0037 | Hash-Chained Audit and Decision Explainability | Observability, Audit, and Operations | Proposed | tasks/observability-audit-operations/hash_chained_audit_explainability_0037.md |
| FEATURE-0038 | Docker and Unraid Deployment Topology | Deployment, Security, and CI | Proposed | tasks/deployment-security-ci/docker_unraid_topology_0038.md |
| FEATURE-0039 | CI/CD and Quality Gates | Deployment, Security, and CI | Proposed | tasks/deployment-security-ci/cicd_quality_gates_0039.md |
| FEATURE-0040 | Secrets and Security Controls | Deployment, Security, and CI | Proposed | tasks/deployment-security-ci/secrets_security_controls_0040.md |

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

## Open Questions

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
