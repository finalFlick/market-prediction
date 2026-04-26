# Session Log

A reverse-chronological journal of working sessions. Each entry: date, who
(human or agent role), what was attempted, what landed, what is blocked.

Format:

```
## YYYY-MM-DD — <session title>
- **Agent**: <Research|Signal|Backtest|Strategy|Risk|Execution|Monitoring|Human>
- **Goal**: one sentence
- **Done**: bullet list of merged changes
- **Verified**: commands run + result (e.g. `pytest -q` → 12 passed)
- **Blocked / next**: bullet list
```

---

## 2026-04-26 — GitHub maintainer settings via `gh` API

- **Agent**: Developer
- **Goal**: Apply repo security and `main` branch protection per
  `gh_cli_maintainer_settings` plan (MCP cannot toggle these).
- **Done**:
  - `PATCH repos/finalFlick/market-prediction` — secret scanning + push
    protection **enabled**.
  - `PUT .../vulnerability-alerts` — **204** (Dependabot alerts on).
  - `PUT .../automated-security-fixes` — **200** `enabled: true` (security
    update PRs on); `security_and_analysis.dependabot_security_updates` now
    **enabled**.
  - `PUT .../branches/main/protection` — required checks (with `\u00b7` in JSON
    to avoid PowerShell corrupting middots), `require_code_owner_reviews: true`,
    1 approval, strict status checks, no force-push, conversation resolution on.
- **Verified**:
  - `gh api repos/finalFlick/market-prediction --jq '.security_and_analysis'`
    → secret_scanning + push_protection enabled; dependabot_security_updates
    enabled.
  - `gh api -i .../vulnerability-alerts` → **204 No Content**.
  - `gh api -i .../automated-security-fixes` → **200** body `enabled: true`.
  - `gh api .../branches/main/protection --jq ...` → contexts include
    `lint · ruff`, …, `Analyze`; `code_owner_review: true`.
- **Blocked / next**:
  - `gh auth refresh -s repo,security_events,workflow` was started for optional
    scope; **`repo` alone sufficed** — cancel device flow if still pending.
  - Merge workflow files to `main` so every required check name exists on
    default branch; first green `main` run validates protection.

## 2026-04-26 — Public GitHub guidance and CI hardening

- **Agent**: Developer
- **Goal**: Record public-repo threat model in steering docs; add maintainer
  contributor guide; Dependabot, CodeQL, CODEOWNERS, composite Python CI setup;
  append `specs/trading-lab-platform` addenda (Requirement E + design/tasks).
- **Done**:
  - Steering: [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md),
    [`.cursor/README.md`](.cursor/README.md),
    [`.cursor/rules/security.mdc`](.cursor/rules/security.mdc),
    [`WORKFLOW.md`](WORKFLOW.md), [`README.md`](README.md),
    [`RUNNING.md`](RUNNING.md) (maintainers pointer).
  - [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) (fork PR + maintainer checklist).
  - GitHub: [`.github/dependabot.yml`](.github/dependabot.yml),
    [`.github/workflows/codeql.yml`](.github/workflows/codeql.yml),
    [`.github/CODEOWNERS`](.github/CODEOWNERS),
    [`.github/actions/setup-trading-lab-python/action.yml`](.github/actions/setup-trading-lab-python/action.yml),
    updated [`.github/workflows/ci.yml`](.github/workflows/ci.yml),
    comment on [`.github/workflows/pages.yml`](.github/workflows/pages.yml).
  - Spec addenda: [`requirements.md`](specs/trading-lab-platform/requirements.md),
    [`design.md`](specs/trading-lab-platform/design.md),
    [`tasks.md`](specs/trading-lab-platform/tasks.md); audit note on
    [FEATURE-0039](specs/trading-lab-platform/tasks/deployment-security-ci/cicd_quality_gates_0039.md).
- **Verified**:
  - `py -3.12 -m pytest tests/cursor_harness -q` → 131 passed
  - `py -3.12 -m ruff check .` → all checks passed
  - `py -3.12 -m pytest -q -m "not slow and not integration and not e2e"` →
    collection `MemoryError` on this host (environment); not attributed to this
    doc/CI-only change set
  - `py -3.12 -m ruff format --check .` / `mypy --strict` → pre-existing issues in
    other paths (unchanged by this session)
- **Blocked / next**: Enable GitHub Rulesets, secret scanning, and Dependabot
  alerts in repo Settings if not already on; confirm `@finalFlick` in CODEOWNERS.

## 2026-04-26 — Swagger `/docs` themed to operator styleguide

- **Agent**: Developer
- **Goal**: Align FastAPI OpenAPI Swagger UI with FEATURE-0034 / Tailwind
  operator-console palette (dark, token-matched) without new dependencies.
- **Done**:
  - Added [`backend/api/static/swagger-trading-lab.css`](backend/api/static/swagger-trading-lab.css)
    with `.swagger-ui` overrides synced to `frontend/tailwind.config.ts`.
  - Updated [`backend/api/app.py`](backend/api/app.py): `docs_url=None`,
    `StaticFiles` on `/static`, custom `GET /docs` via `get_swagger_ui_html`
    and `syntaxHighlight.theme: obsidian`.
  - Extended [`tests/e2e/test_api_app.py`](tests/e2e/test_api_app.py) with
    Swagger HTML and CSS smoke tests.
  - Documented `/docs` in [`RUNNING.md`](RUNNING.md); addenda in
    [`specs/trading-lab-platform/tasks.md`](specs/trading-lab-platform/tasks.md)
    and [`FEATURE-0034`](specs/trading-lab-platform/tasks/frontend-operator-experience/style_guide_component_library_0034.md).
- **Verified**:
  - `py -3.12 -m pytest tests/e2e/test_api_app.py -q` → 9 passed
  - `py -3.12 -m ruff check backend/api/app.py tests/e2e/test_api_app.py` →
    all checks passed
  - `py -3.12 -m mypy --strict backend/api/app.py tests/e2e/test_api_app.py` →
    success
  - `py -3.12 -m pytest -q` → `294 passed, 3 warnings in 234.42s`
- **Blocked / next**: Theme `/redoc` in a follow-up if operators want parity.

## 2026-04-26 — dev-speed docker, MVP-0 run UI audit, and Cursor workflow hardening

- **Agent**: Developer
- **Goal**: Finalize the session's MVP-0 run/API/UI and Docker development
  changes, audit them into `specs/trading-lab-platform`, strengthen the weak
  frontend styleguide, improve `.cursor` guidance based on observed workflow
  failures, and commit the completed work.
- **Done**:
  - Added shared Docker base workflow: `Dockerfile.base`,
    `Dockerfile.research`, dev compose override, `dev.py`, and docs for the
    fast Docker development loop.
  - Refactored backend and trading-engine Dockerfiles to inherit from
    `trading-base`.
  - Added Windows Docker Desktop bind-mount masks for `.venv`, `.git`, caches,
    and frontend generated folders after measuring them as the cause of the
    15+ minute pytest run.
  - Audited current work in
    `specs/trading-lab-platform/tasks.md` and added notes to FEATURE-0003 and
    FEATURE-0038.
  - Rewrote FEATURE-0034 as a build-ready cyberpunk hacker styleguide and
    component-library spec with tokens, layout patterns, component categories,
    demo data expectations, and validation gates.
  - Made `dev.py` stdlib-only after validation showed bare Windows Python did
    not have `click`, preserving the same CLI commands without host setup.
  - Switched frontend Docker installs to the committed lockfile (`npm ci`) and
    made the dev frontend command populate the `trading-node-modules` volume on
    first start.
  - Made dev dependency volume names explicit so `dev.py reset-deps` removes
    the same volumes Compose mounts.
  - Added dev-only `types-PyYAML==6.0.12.20260408` after checking PyPI current
    metadata (released 2026-04-08, Python >=3.10, tested with mypy 1.20) so
    the container mypy gate is reproducible.
  - Added `.cursor/rules/component-first.mdc`, strengthened frontend/docker
    rules, corrected hook-router semantics in `.cursor/hooks/README.md`, and
    expanded `.cursor/context-router.json` routing for styleguide and Windows
    Docker prompts.
  - Updated `README.md`, `RUNNING.md`, `docs/UI_REQUIREMENTS.md`, and `TODO.md`
    so future agents can resume from the current state.
- **Verified**:
  - `docker build -f Dockerfile.base -t trading-base .` → success; subsequent
    cached rebuild took ~2.8 s.
  - `docker compose -f docker-compose.yml -f docker-compose.dev.yml build` →
    success after `trading-base` existed.
  - `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d` →
    backend, frontend, research, engine, redis, and duckdb started.
  - Backend health check via PowerShell `Invoke-WebRequest` →
    `200 {"status":"ok", ...}`.
  - Backend hot reload verified from logs:
    `WatchFiles detected changes in 'backend/api/routers/runs.py'. Reloading...`.
  - Windows bind-mount investigation: `/app` visible tree dropped from ~3 GB to
    5.7 MB; `du /app` dropped from 104 s to 1.4 s.
  - Dev-container unit suite:
    `pytest -q -m "not slow and not integration"` →
    `291 passed, 1 deselected, 3 warnings in 53.24s`.
  - Dev-container full suite: `pytest -q` →
    `292 passed, 3 warnings in 52.89s`.
  - Security suite: `pytest tests/security -q` → `25 passed`.
  - Research container import smoke:
    `torch=2.11.0+cu130`, `lightgbm=4.6.0`, `vectorbt=1.0.0`,
    `xgboost=3.2.0`.
  - `docker compose ... down` then `up -d` with preserved volumes → 24.7 s.
  - `ruff check dev.py` → all checks passed.
  - `mypy --strict --explicit-package-bases dev.py` → success.
  - `python dev.py --help` on host Windows Python → displays command help
    without requiring `click`.
  - `docker compose ... exec frontend npm run typecheck` → success.
  - `docker compose ... exec -e NODE_ENV=production frontend npm run build` →
    success; 19 app routes generated/validated.
  - `docker compose -f docker-compose.yml -f docker-compose.dev.yml build frontend`
    → success; production image builds with `npm ci` and Next standalone output.
  - `mypy --strict --explicit-package-bases data research strategies risk
    backtests execution monitoring backend runs learning dev.py` → success
    after installing the pinned PyYAML stubs.
- **Blocked / next**:
  - Production compose now expects a locally tagged `trading-base`; CI should
    build/tag it explicitly or move to a compose target/registry-cache pattern.
  - `/styleguide` itself is not implemented yet; FEATURE-0034 is now strong
    enough to drive that implementation.
  - Full global `ruff check .`, `mypy --strict .`, frontend lint/typecheck/build,
    e2e, and backtest smoke still need to be run or remediated before a release
    PR is considered complete.

---

## 2026-04-25 — no-key MVP slice (ingest, optional Redis, spec addendum)

- **Agent**: Developer
- **Goal**: Public REST ingesters without exchange keys, optional Redis with in-memory event bus, operator env docs, spec addendum; ship 0.3.1.
- **Done**:
  - `data/ingest/binance_public.py`, `coinbase_public.py`, `yfinance_source.py`; `data/ingest/run.py` `--source`; `Exchange.YAHOO`; `yfinance` in `dev` + `public-data` extra.
  - `backend/api/routers/system.py` `redis_disabled`; `runs/events/*`; frontend health badges; e2e `test_health_redis_optional`.
  - `tests/data/`, `tests/runs/test_in_memory_bus.py`; `tests/security/test_no_secrets.py` git-tracked `.env` only.
  - `docs/REMINDERS.md`, `.env.example`, `RUNNING.md`; `specs/trading-lab-platform` requirements/design/tasks addendum + FEATURE-0041–0043.
  - `CHANGELOG` 0.3.1, `pyproject` 0.3.1.
- **Verified**:
  - `py -3.12 -m pytest -q` → 265 passed
  - `py -3.12 -m pytest -q -m e2e` → 10 passed
  - `ruff check .` → pass; `mypy --strict --explicit-package-bases .` → 168 files
  - `py -3.12 -m backtests.smoke` → smoke OK; `py -3.12 -m monitoring.audit verify --tables critical` → all_ok
- **Blocked / next**: n/a

## 2026-04-25 — mvp-0 build slice (full stack)

- **Agent**: Developer
- **Goal**: Complete MVP-0 build slice: quality gates, invariants, runs/learning/audit/backend/frontend, acceptance e2e, docs, DEC-007/008/009, v0.3.0.
- **Done**:
  - **Schema fix:** Renamed `state_transitions` column `at` → `transitioned_at` (DuckDB reserved/parse conflict).
  - `monitoring.canonical_json`, backtest det smoke anchor, `pytest -m det`, hash-chain `ha_*` + `monitoring.audit verify`.
  - `RiskAudit` / `RiskDecision`, `data/repositories/audit/duckdb_risk_audit.py`, security scans (path-only risk, no bypass in app roots, `runs/` LLM isolation).
  - `runs/` (RunConfig, orchestrator, recovery, outbox), `execution` reconcile stub, `learning/` OOS scorers, `data/seeds` + `adjust` helpers.
  - API: runs list, health+audit+metrics, kill-switch; frontend kitsune + MVP-0 pages.
  - `docs/MVP0_READINESS.md`, `CHANGELOG` 0.3.0, `DECISIONS` DEC-007/008/009, `pyproject` 0.3.0.
- **Verified**:
  - `ruff check .` → all checks passed
  - `mypy --strict --explicit-package-bases .` → Success (155 source files)
  - `py -3.12 -m pytest -q` → 256 passed
  - `py -3.12 -m backtests.smoke` → smoke OK
  - `py -3.12 -m monitoring.audit verify --tables critical` → all_ok: true
- **Blocked / next**: n/a

## 2026-04-25 — merge docsite worktree into main

- **Agent**: Developer
- **Goal**: Re-integrate the `experiment/specs-gh-pages` worktree
  (`market-prediction-pages`) into `main` and remove the split.
- **Done**:
  - Merged `experiment/specs-gh-pages` (`mkdocs.yml`, `docsite/`,
    `.github/workflows/pages.yml`).
  - Added `docsite/` to `ruff` and `mypy` excludes in `pyproject.toml`.
  - Removed sibling worktree and the local + remote
    `experiment/specs-gh-pages` branch.
- **Verified**: `ruff check .`, `mypy --strict --explicit-package-bases .`,
  `pytest -q`, `pytest -q -m e2e`.
- **Blocked / next**: Pages workflow now publishes from `main`.

## 2026-04-25 — docsite README for GitHub Pages

- **Agent**: Developer
- **Goal**: Add a maintainer-facing `docsite/README.md` for the Pages/MkDocs
  pipeline (distinct from repo root `README.md`) and link it from `index.md`.
- **Done**: `docsite/README.md`; `docsite/index.md` maintainer link.
- **Verified**: `mkdocs build` in worktree (success).
- **Blocked / next**: none.

## 2026-04-25 — trading-lab spec site (MkDocs + GitHub Pages, worktree)

- **Agent**: Developer
- **Goal**: Add a themed MkDocs + GitHub Pages deploy for
  `specs/trading-lab-platform/` and project docs, entirely on
  `experiment/specs-gh-pages` in a sibling git worktree so `main` stays
  untouched by other agent work.
- **Done**:
  - Sibling worktree: `../market-prediction-pages` on
    `experiment/specs-gh-pages`.
  - `mkdocs.yml` + `docsite/` (index, kitsune-cyberpunk `extra.css`, sync
    hook, mermaid `fence_div_format` + `javascripts/mermaid-init.js`, pinned
    `docsite/requirements.txt` — not in `pyproject.toml`).
  - `.github/workflows/pages.yml` (path-filtered push, `concurrency: pages`,
    `actions/deploy-pages@v4` + `upload-pages-artifact@v3`).
- **Verified**:
  - `py -3.12 -m pip install -r docsite/requirements.txt` in worktree
  - `py -3.12 -m mkdocs build` in worktree (success; link warnings to
    out-of-doc paths like `.cursor/` expected)
  - Built HTML contains `<div class="mermaid">` in
    `specs/trading-lab-platform/design/`
  - `git push` → branch `experiment/specs-gh-pages` on `origin`
  - `gh api ... deployment-branch-policies` → allowed
    `experiment/specs-gh-pages` on environment `github-pages` (unblocks
    `actions/deploy-pages@v4` with that environment)
  - GitHub Actions run `pages` (run id `24939587230`) → success (build + deploy)
  - `gh api .../pages` → `https://finalflick.github.io/market-prediction/`
  - Live home page fetches and shows themed “Trading Lab — spec library”
- **Blocked / next**:
  - Rebase the worktree on `origin/main` when you want the latest spec content
    (`git fetch origin && git rebase origin/main` in
    `../market-prediction-pages`).
  - If you merge this into `main`, add `docsite/` to ruff/mypy excludes
    in `pyproject.toml` (per plan).

## 2026-04-25 — mvp-0 live broker registration lock slice

- **Agent**: Developer
- **Goal**: Implement the MVP-0 live broker registration lock contract from
  `specs/trading-lab-platform` with TDD and runner integration.
- **Done**:
  - Added `execution/brokers/registry.py` with
    `LiveBrokerRegistry` and `LiveAdapterRegistrationForbidden`.
  - Added `configs/runtime.yaml` with default
    `live_adapters_unlocked: false`.
  - Added `BinanceLive` / `CoinbaseLive` aliases for design parity.
  - Updated `execution/runner.py` to register paper by default and reject
    locked live brokers with a clear Click error.
  - Added `tests/security/test_live_registration_forbidden.py` (5 tests).
  - Added resolution notes to FEATURE-0021 and FEATURE-0022 task files.
  - Added `DEC-006` and created `CHANGELOG.md`; bumped version to `0.2.0`.
- **Verified**:
  - `py -3.12 -m pytest -q tests/security/test_live_registration_forbidden.py`
    → 5 passed
  - `py -3.12 -m pytest -q tests/security/` → 21 passed
  - `py -3.12 -m pytest -q -m "not slow and not integration"` → 204 passed
  - `ruff check execution/brokers/registry.py execution/runner.py tests/security/test_live_registration_forbidden.py` → all checks passed
  - `py -3.12 -m mypy --strict execution/brokers/registry.py execution/runner.py tests/security/test_live_registration_forbidden.py` → success
  - `py -3.12 -c "import execution.brokers.binance, execution.brokers.coinbase; print('ok')"` → ok
  - `ruff check .` → fails on pre-existing unrelated issues in
    `.cursor/hooks/check_dependency_research.py`, `backtests/engine.py`,
    and `monitoring/logger.py`.
- **Blocked / next**:
  - Continue Wave 1 with FEATURE-0039 (CI/CD quality gates) so global lint and
    typecheck regressions are enforced systematically.

---

## 2026-04-25 — trading-lab-platform task system

- **Agent**: Planner / Spec
- **Goal**: Convert the approved `trading-lab-platform` requirements and
  design into an epic and feature ticket system that explains why/what,
  not implementation how.
- **Done**:
  - Replaced the placeholder `specs/trading-lab-platform/tasks.md` with an
    execution index, roadmap, assumptions, traceability matrix, open
    questions, and quality checklist.
  - Added `specs/trading-lab-platform/tasks/` with 12 epic folders and 40
    feature tickets covering MVP-0, v1, and later gated work.
  - Recorded the `.kiro` path mismatch as an assumption: this repo's active
    spec tree is `specs/trading-lab-platform/`.
  - Updated `TODO.md` to point implementation agents at the new task system.
- **Verified**:
  - `Glob specs/trading-lab-platform/tasks/**/*.md` → 52 Markdown files
    found (12 epics + 40 feature tickets).
  - Generated link check over `specs/trading-lab-platform/tasks.md` →
    `indexed_paths=52 unique_paths=52 missing=0`.
  - `ReadLints` on `specs/trading-lab-platform/tasks.md` and
    `specs/trading-lab-platform/tasks/` → 0 linter errors.
- **Blocked / next**:
  - Full code validation (`pytest -q`, `ruff check .`, `mypy --strict .`)
    was not run because this session only changed planning Markdown.
  - Next implementation agents should start with Wave 1 in
    `specs/trading-lab-platform/tasks.md`.

---

## 2026-04-25 — trading-lab-platform spec finalization + de-risking POCs

- **Agent**: Human + Architect (planner) + scripted POC runner
- **Goal**: Finish the `trading-lab-platform` spec session through Phase 2
  (design) at production quality, then run a quick set of throwaway POCs
  to expose any gap before tasks.md.
- **Done**:
  - `specs/trading-lab-platform/requirements.md` — added top-level
    `Phasing` section and inline `[MVP-0] / [v1] / [v1.x] / [v1.1] /
    [v1.2-4] / [v2.x] / [FUTURE]` tags across Reqs 4, 5, 11, 16, 18,
    21, 22, 26, 33, 41, 44 so nothing was deleted while v1+ scope
    moved off the MVP-0 slab.
  - `specs/trading-lab-platform/design.md` — new `MVP-0 Scope and
    Sequencing` section (Day-0 Invariants, Deliverables, Acceptance,
    12-step v1 plan); Canonical-JSON serialization spec in §9; staggered
    hash-chain (critical tables only at MVP-0) in §15; `LiveBrokerRegistry`
    + `LiveAdapterRegistrationForbidden` for Coinbase/Binance until
    v1.1; LLM calibration split by `task_type`; Schwab CSV-first +
    OAuth `[v1.x]`; long-horizon single-stock equities flagged
    `degraded` + capped at R-1 until v1.4.
  - 11 throwaway POC scripts under `pocs/` (deterministic backtest,
    risk-bypass toy + real-engine, artifact replay, event stream +
    DuckDB/SQLite outbox, paper broker fees/slippage/partial,
    LLM isolation, config snapshot, learning-loop scoreboard,
    quants-first signal experiments, latency + 1M-row pipeline)
    plus `pocs/run_all_pocs.py`. `poc_results.md` summarises the run.
  - `pyproject.toml` — added `pocs` to `[tool.ruff] extend-exclude`
    so throwaway code never gates the strict ruleset.
  - Targeted spec deltas motivated by POC 8 (learning loop):
    - `requirements.md` Req 44.9 (new): every lever scorer consumes
      OOS / purged-embargo outcomes only; raw IS PnL forbidden;
      `tests/learning/test_no_in_sample_scoring.py` enforces.
    - `design.md` Component 15: matching implementation note tying
      `Scorer.update()` to `RunSummary.oos_metrics` with a typed
      Pydantic boundary, citing the POC.
- **Verified**:
  - `ReadLints` on `requirements.md`, `design.md`, `pyproject.toml`
    → 0 errors after every change.
  - `python pocs/run_all_pocs.py` → 11/11 `OK` (POC 2b cleanly
    `SKIP`s when project deps aren't in the active interpreter).
  - `ruff check .` → only 2 pre-existing warnings in
    `backtests/engine.py` and `monitoring/logger.py`; `pocs/` no
    longer surfaces in default sweeps.
  - File-size sanity: `requirements.md` 1371 → 1465 lines (+94,
    additive); `design.md` 4026 → 4639 lines (+613, additive);
    no requirement or design section removed.
- **Blocked / next**:
  - Phase 3 (`tasks.md`) for `trading-lab-platform` is still pending;
    user has not yet approved the design for that step.
  - Real `RiskEngine` POC (`pocs/risk_engine_bypass/run_poc_real.py`)
    needs a 3.11 venv with `pip install -e .` to run end-to-end;
    optional CI job once that venv exists.
  - Test stubs `tests/security/test_live_registration_forbidden.py`
    and `tests/learning/test_no_in_sample_scoring.py` are referenced
    by Reqs 4.6 and 44.9 but not yet implemented; they belong in
    `tasks.md`.

---

## 2026-04-25 — prompt-context-router (spec session)

- **Agent**: Human + planner / developer / tester subagents
- **Goal**: Auto-inject relevant `.cursor` steering-file excerpts into the
  agent's context, both at session start and dynamically during a chat,
  via Cursor hooks.
- **Done**:
  - Spec session under `specs/prompt-context-router/` with
    `requirements.md`, `design.md`, `tasks.md`.
  - Two new hook scripts:
    - `.cursor/hooks/prompt_capture.py` (`beforeSubmitPrompt`) — persists
      the user prompt (redacted, capped at 8 KB) to
      `.cursor/state/last-prompt.json`.
    - `.cursor/hooks/prompt_context_router.py` (`postToolUse`) — reads
      the captured prompt + tool call, evaluates a routing table, and
      emits `additional_context` snippets.
  - Pure routing core split into `_router_types.py`, `_router_io.py`,
    `_router_core.py` (load/validate, match, excerpt, prune, route) —
    stdlib only, fail-open everywhere.
  - Routing table at `.cursor/context-router.json` (v1, 9 rules:
    risk-policy, evaluation-gates, signal-research, data-ingest,
    frontend-dashboard, infra-deployment, llm-isolation, spec-workflow,
    workflow-discipline).
  - `session_init.py` augmented with a "Steering files (read on demand)"
    doc map and a "How to invoke" pointer to the `session-init` skill;
    bumped `MAX_CONTEXT_CHARS` 6000 → 8000.
  - Wired both hooks into `.cursor/hooks.json` (5 s timeout, fail-open).
  - Operator doc at `.cursor/hooks/README.md`; linked from
    `PROJECT_CONTEXT.md`.
  - Runtime state files added to `.gitignore`.
  - Spec-driven semantic refinement: trigger keys in routing rules are
    OR-combined (was AND-between-keys). `tool_name_in` remains an
    AND filter. Spec docs and tests updated to match.
  - 16 new test files under `tests/cursor_harness/` covering
    routing-table sanity, load/validate, match, excerpt, prune, route,
    determinism, hook-contract subprocess tests, hooks.json schema,
    session-init doc map, and an end-to-end smoke test.
- **Verified**:
  - `ruff check .cursor/hooks tests/cursor_harness` → All checks passed
  - `python -m pytest tests/cursor_harness/ -q` → 100 passed in 2.85s
  - Live smoke: `prompt_capture` + `prompt_context_router` end-to-end
    against the real project: prompt-only trigger injects
    `docs/RISK_POLICY.md` + `.cursor/rules/risk-management.mdc`;
    tool-only trigger (`Read backtests/run.py`) injects
    `docs/EVALUATION.md`; unrelated paths emit `{}` cleanly;
    session-memory dedup confirmed by repeating the same call.
  - `mypy --strict` not run: not installed in the local Python 3.9
    interpreter (project requires 3.11+); annotations were authored
    against `mypy --strict` in mind and are exercised at runtime by
    the test suite.
- **Blocked / next**:
  - Run `pytest`, `ruff`, `mypy` on a 3.11+ environment in CI to
    confirm the broader project suite still passes.
  - Optional follow-up: a small `mypy.ini` override or a
    `tests/cursor_harness/test_router_typing.py` driver that runs
    `mypy --strict` on the hooks dir, once a 3.11 venv is available.

## 2026-04-25 — Initial scaffolding

- **Agent**: Human + scaffolding agent
- **Goal**: Stand up the repository skeleton, rules, agent definitions, and a
  modular Python package layout for the full pipeline.
- **Done**:
  - Created repo structure (`data/`, `research/`, `strategies/`, `risk/`,
    `backtests/`, `execution/`, `monitoring/`, `docs/`, `configs/`, `tests/`).
  - Wrote `.cursor/rules/` (architecture, coding-standards, research-workflow,
    backtesting).
  - Wrote `AGENTS.md`, `TODO.md`, `DECISIONS.md`, `SIGNALS.md`,
    `docs/DESIGN.md`, `docs/STRATEGY.md`.
  - Wrote skeleton modules (interfaces + stubs) for each pipeline stage.
  - `pyproject.toml` with the agreed stack.
- **Verified**: `python -c "import data, research, strategies, risk, backtests, execution, monitoring"` imports without error.
- **Blocked / next**: Begin Milestone 1 — data ingestion (`data/ingest/binance.py`).
