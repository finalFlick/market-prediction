# FEATURE-0038: Docker and Unraid Deployment Topology

## Parent Epic

deployment-security-ci

## Status

Proposed

## Summary

Define the self-hosted service topology, container boundaries, networks, health checks, and GPU/Ollama assumptions.

## Why

The core platform must run reliably on the operator's Unraid environment without cloud-only dependencies.

## What

A deployment capability covering compose services, external dependencies, volumes, non-root containers, health checks, and startup order.

## User / System Story

As a platform operator or implementation agent,
I want docker and unraid deployment topology,
so that the trading-lab platform can satisfy the related requirements with evidence.

## Source Traceability

- requirements.md: Req 37, 39, 40
- design.md: Deployment Topology; Containerization Strategy; Single-Host Note; Recommended Stack
- Repo conventions: .cursor/rules/architecture.mdc, .cursor/rules/security.mdc, .cursor/rules/workflow.mdc, .cursor/rules/spec-sessions.mdc, and AGENTS.md.

## Requirements Covered

- Req 37
- Req 39
- Req 40

## Design Alignment

Deployment Topology; Containerization Strategy; Single-Host Note; Recommended Stack. This feature states the expected capability and review evidence without prescribing code-level implementation details beyond the design and project rules.

## In Scope

- The behavior, outcome, or platform capability described above.
- Traceability to listed requirements and design sections.
- Validation expectations appropriate to the affected pipeline stage.
- Documentation and diagnostics needed for review and operation.

## Out of Scope

- Implementation code.
- Exact file-level steps unless already mandated by design.md.
- Later-phase capabilities not listed in the source traceability.
- Any change that bypasses risk, weakens LLM isolation, or breaks the one-way pipeline.

## Acceptance Criteria

- Given the source documents and repo standards, when an implementation plan is prepared, then it traces this feature to the listed requirements and design sections.
- Given the feature is implemented, when validation runs, then the expected tests and checks listed below pass with command/result evidence.
- Given unsupported or later-phase behavior is requested, when the system handles it, then it rejects, defers, or marks it explicitly rather than silently enabling it.

## Validation Expectations

- compose config validation; container boot smoke; health check review
- Stage-appropriate unit, integration, contract, e2e, safety, or smoke tests.
- Final implementation evidence should include pytest -q, ruff check ., and mypy --strict . unless the approved task narrows verification with a documented reason.

## Dependencies

- Dockerfiles; docker-compose.yml; .env.example

## Risks / Edge Cases

- External Ollama/Hermes dependencies can be misconfigured.
- Phase boundaries must remain visible in implementation and docs.
- Reviewers must confirm validation evidence is real, not aspirational.

## Observability / Diagnostics

The implementation should expose enough logs, metrics, audit records, UI state, or artifact metadata for an operator or reviewer to determine whether the feature is active, healthy, degraded, rejected, or deferred. Diagnostics must avoid logging secrets and preserve the auditability expectations in design.md.

## Documentation Expectations

- Update operator or developer documentation when the feature changes a workflow, command, route, config surface, or safety policy.
- Update DECISIONS.md if implementation changes architecture, risk posture, phase scope, or release gates.
- Update SESSION_LOG.md with verification evidence when implementation work lands.

## Done Means

- [ ] The feature outcome is implemented or explicitly marked as deferred according to its phase.
- [ ] Acceptance criteria above are satisfied with evidence.
- [ ] Validation expectations are covered by tests, smoke checks, or documented manual verification.
- [ ] Source traceability remains accurate after implementation.
- [ ] Required docs, decisions, and session log entries are updated.

## Session Audit Note - 2026-04-26

The dev-speed Docker overhaul partially advances this feature:

- Added shared `trading-base` image (`Dockerfile.base`) so backend, engine, and research reuse the expensive Python dependency layer.
- Added `Dockerfile.research` and a `research` compose service for ad-hoc training/Jupyter.
- Added `docker-compose.dev.yml` with source bind-mounts, named dependency volumes, backend hot reload, frontend HMR, and Jupyter.
- Added Windows Docker Desktop bind-mount masks for host-only directories (`.venv`, `.git`, caches, `frontend/node_modules`) after measuring `/app` shrink from ~3 GB to 5.7 MB and pytest improvement from 928 s/incomplete to ~53 s passing.

This remains **partial** for FEATURE-0038 because production CI/build orchestration still needs an explicit `trading-base` build/tag step or registry cache strategy.
