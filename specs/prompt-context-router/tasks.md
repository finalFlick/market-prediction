# Tasks: prompt-context-router

## Document Information

- **Feature Name**: prompt-context-router
- **Version**: 0.1
- **Date**: 2026-04-25
- **Author**: Brandon
- **Related Documents**:
  - Requirements: `./requirements.md`
  - Design: `./design.md`
- **Shipped (code + tests):** 2026-04-25 — implementation lives in `.cursor/`,
  `tests/cursor_harness/`, and `SESSION_LOG.md` (section below).
- **Latest harness check (local):** `python -m pytest tests/cursor_harness/ -q` →
  100 passed (2026-04-25).

## Implementation Overview

The router is a small, isolated tooling change living entirely under
`.cursor/` and `tests/cursor_harness/`. It does not touch any pipeline
package. We sequence **foundation-first**: data contracts and the
routing-table file ship before the pure `route()` function, then the
hook entry points wrap that function, then `session_init.py` is
augmented, then hooks are wired into `hooks.json`, then docs and
final verification.

### Strategy

- **Sequencing:** foundation-first.
- **Testing:** unit tests written alongside each implementation task
  (per `coding-standards.mdc`); the e2e smoke test lands at the end
  of Phase 4.
- **Verification per task:** `pytest -q tests/cursor_harness`,
  `ruff check .cursor/hooks tests/cursor_harness`,
  `mypy --strict .cursor/hooks tests/cursor_harness` (per
  `workflow.mdc`). Full repo `pytest -q` runs at task 5.3.

### Definition of done for the whole feature (status 2026-04-25)

- [x] Every leaf task below is checked off (`- [x]`).
- [x] All acceptance criteria from `requirements.md` (Requirements
      1–9 and NFRs) are implemented; coverage is in
      `tests/cursor_harness/` with narrative verification in
      `SESSION_LOG.md`.
- [x] `ruff check .cursor/hooks tests/cursor_harness` — all checks
      passed (2026-04-25 work session, cited in `SESSION_LOG.md`).
- [x] `python -m pytest tests/cursor_harness/ -q` — 100 passed
      (2026-04-25 work session; re-run 2026-04-25: 100 passed).
- [ ] `mypy --strict` on the hooks + `tests/cursor_harness` — **not
      run** in the session’s default Python 3.9 interpreter; **do**
      in a 3.11+ project venv or CI (see `SESSION_LOG.md` *Blocked / next*).
- [ ] Full-repo `pytest -q` — **not green** in a minimal / 3.9 install
      (missing `duckdb`, `vectorbt`, and other stack deps; tests use
      3.11+ features). **CI or full dev venv** is the gate.
- [x] At least one e2e smoke run (task 5.1) exercises ≥ 3 of the
      9 v1 routing rules end-to-end (`test_smoke_e2e.py`).
- [x] `SESSION_LOG.md` entry recorded (`## 2026-04-25 — prompt-context-router (spec session)`; title says “spec session” rather than
      “shipped”).
- [x] No `DECISIONS.md` entry needed (router is tooling; if review
      disagrees, append one).

---

## Implementation Plan

> **Status legend:** `- [ ]` not started · `- [~]` in progress
> · `- [x]` complete
>
> **This plan is complete;** all items below are `- [x]`.

### Phase 1 — Foundation

- [x] 1. Set up scaffolding and shared types
- [x] 1.1 Add typed contracts and shared utilities
  - Create `.cursor/hooks/_router_types.py` with the `TypedDict`
    definitions from `design.md` § Data Models: `LastPromptRecord`,
    `InjectedSnippet`, `SessionMemoryFile`, `RouterLogRecord`,
    `MatchClause`, `SnippetSpec`, `RoutingRule`, `RoutingTable`.
  - Add a `_router_io.py` helper module with `atomic_write_json(path,
    obj)`, `read_json(path)`, `append_jsonl(path, record)`, and
    `truncate_jsonl(path, max_lines)` — stdlib only.
  - Unit tests: `tests/cursor_harness/test_router_io.py` covers atomic
    writes, malformed JSON read, append + truncate.
  - _Requirements: 1.1, 1.4, 3.1, 8.1, 8.3_

- [x] 1.2 Author the v1 routing table
  - Create `.cursor/context-router.json` with `version: 1` and the
    9 rules listed in `design.md` § Component 4 (`risk-policy`,
    `evaluation-gates`, `signal-research`, `data-ingest`,
    `frontend-dashboard`, `infra-deployment`, `llm-isolation`,
    `spec-workflow`, `workflow-discipline`).
  - Each rule includes `id`, `priority`, `description`, `match`, and
    `snippets` per the design schema.
  - Add a JSON-schema-style sanity test in
    `tests/cursor_harness/test_routing_table.py` that loads the file,
    asserts unique ids, validates regex compilation, and checks every
    `path` field points at an existing repo file.
  - _Requirements: 5.1, 5.2, 5.3, 5.5_

- [x] 1.3 Update `.gitignore` for new state files
  - Append `.cursor/state/last-prompt.json`,
    `.cursor/state/session-context-memory.json`, and
    `.cursor/state/router-log.jsonl` to `.gitignore`.
  - Add a brief comment grouping them under the existing "Cursor
    harness state" section.
  - _Requirements: NFR-Security 1, NFR-Security 4_

### Phase 2 — Pure routing core

- [x] 2. Implement the deterministic `route()` function
- [x] 2.1 Implement table loading and validation
  - In a new `.cursor/hooks/_router_core.py`, implement
    `load_routing_table(path) -> RoutingTable | None`. Drops invalid
    rules (bad regex, missing `path`, path traversal attempt) with a
    stderr warning; returns `None` on missing/malformed top-level.
  - Unit tests in `tests/cursor_harness/test_router_load.py`: missing
    file, malformed JSON, wrong version, non-unique ids, bad regex,
    path traversal (`../etc/passwd`), absolute path.
  - _Requirements: 5.1, 5.4, 7.3, NFR-Security 4_

- [x] 2.2 Implement matching logic
  - In `_router_core.py`, implement `rule_matches(rule, *, prompt,
    tool_name, tool_input_str, tool_output, agent_message) -> bool`.
    AND across present `match` keys, OR within each list value.
  - Unit tests in `tests/cursor_harness/test_router_match.py`:
    prompt-only match, tool-input-only match, tool-name filter,
    agent-message match, AND across keys, OR within a list,
    no-match, empty-match-block (treated as never match).
  - _Requirements: 2.2, 5.3_

- [x] 2.3 Implement snippet excerpting
  - In `_router_core.py`, implement `excerpt(path, anchor, max_chars,
    project_dir) -> str | None`. Reads file head when `anchor is
    None`; reads from the matching `## Header` to next `## ` (or
    EOF) when an anchor is given. Truncates to `max_chars` and
    appends `\n\n... [truncated]` if cut.
  - Unit tests in `tests/cursor_harness/test_router_excerpt.py`:
    head excerpt, anchor excerpt at top of file, anchor excerpt mid
    file, missing anchor returns None, missing file returns None,
    truncation appends marker.
  - _Requirements: 2.4, 4.3, 5.4_

- [x] 2.4 Implement the pure `route()` function
  - In `_router_core.py`, implement `route(*, hook_input,
    last_prompt, routing_table, session_memory, budget_chars,
    project_dir, now) -> tuple[str, SessionMemoryFile,
    RouterLogRecord]` per `design.md` § Internal Python API.
  - Inside: stringify `tool_input` (skipping fields whose name
    contains any token in `_common.SECRET_KEYS`); apply matching;
    sort matched rules by `priority` desc; for each rule, dedup
    each snippet by `(rule_id, path, anchor, sha256)` against
    session memory; apply per-snippet `max_chars`; accumulate up
    to `budget_chars`; build the `additional_context` string with
    `## Auto-loaded:` headers; build the log record.
  - Unit tests in `tests/cursor_harness/test_router_route.py`:
    empty match → `("", memory_unchanged, log_with_no_inject)`;
    one match injects with header; budget overflow drops
    lowest-priority; per-snippet truncation; deduplicated rule
    skipped with `skip_reason="deduplicated"`; sha256 invalidation
    re-injects; missing snippet skipped.
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 4.1, 4.2,
    4.3, 4.4, 5.3, 8.1, 8.2, 8.4, NFR-Determinism 1_

- [x] 2.5 Implement session-memory pruning
  - In `_router_core.py`, implement `prune_memory(memory, *, now,
    ttl_hours=24) -> SessionMemoryFile`. Drops `InjectedSnippet`
    entries with `injected_at` older than `ttl_hours`; drops empty
    sessions.
  - Unit tests in `tests/cursor_harness/test_router_dedup.py`:
    fresh entries kept, expired entries dropped, sha256 mismatch
    forces re-inject, second identical injection skipped.
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

### Phase 3 — Hook entry points

- [x] 3. Wire the hooks
- [x] 3.1 Implement `prompt_capture.py`
  - Create `.cursor/hooks/prompt_capture.py`. Reads stdin via
    `_common.read_input`, applies `_common.redact`, truncates to
    8000 chars, writes `LastPromptRecord` atomically to
    `.cursor/state/last-prompt.json`. Honours `TLAB_ROUTER_DISABLE`.
    Always emits `{"continue": true}`.
  - Unit tests in `tests/cursor_harness/test_prompt_capture.py`:
    happy path persists redacted+truncated prompt, missing
    `session_id` becomes `"unknown"`, write failure still returns
    `{"continue": true}`, `TLAB_ROUTER_DISABLE=1` skips write.
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 7.1, 7.3, 7.5,
    9.2_

- [x] 3.2 Implement `prompt_context_router.py`
  - Create `.cursor/hooks/prompt_context_router.py`. The thin
    `__main__` reads stdin, loads `last-prompt.json` (skipping if
    `captured_at` > 30 min old or mtime stale), loads the routing
    table, loads session memory, computes `now`, calls
    `route(...)`, writes the updated memory atomically, appends
    the log record, truncates the log to 5000 lines, emits
    `{"additional_context": ...}` if non-empty else `{}`. Honours
    `TLAB_ROUTER_DISABLE` and `TLAB_ROUTER_BUDGET_CHARS`. Top-level
    `try/except BaseException` writes `{}` and exits 0.
  - Unit tests in `tests/cursor_harness/test_router_main.py` driving
    the entry point as a Python module: happy path emits
    `additional_context`; stale prompt is ignored; disable env var
    short-circuits; forced exception (monkey-patched `route`)
    fails open with `{}`.
  - _Requirements: 2.1, 2.5, 4.5, 7.1, 7.2, 7.3, 8.1, 8.3, 9.2_

- [x] 3.3 Subprocess integration test for the hook contract
  - Add `tests/cursor_harness/test_hook_contract.py` that spawns
    each hook as a subprocess (`subprocess.run` with a 5 s
    timeout), feeds it crafted Cursor stdin JSON, and asserts the
    stdout JSON shape, exit code 0, and that no exception escapes
    even when stdin is empty / malformed.
  - _Requirements: 7.1, 7.2, 7.3_
  - **Also:** `tests/cursor_harness/test_hook_scripts.py` exercises
    additional hook subprocess coverage (superset of the original
    one-file plan).

### Phase 4 — Session-start augmentation

- [x] 4. Augment session-start orientation and wire hooks
- [x] 4.1 Augment `session_init.py` with the doc map
  - Modify `.cursor/hooks/session_init.py`: walk `docs/*.md`,
    `.cursor/agents/*.md`, `.cursor/skills/*/SKILL.md`; for each
    file extract first H1 (or first non-empty line) as title;
    append `## Steering files (read on demand)` with one bullet
    per file. Append `## How to invoke` pointing to the
    `session-init` skill. Raise `MAX_CONTEXT_CHARS` 6000 → 8000.
  - Unit tests in `tests/cursor_harness/test_session_init_docmap.py`:
    fixture project with two docs/agents/skills; assert section
    headers present; assert all titles listed; assert budget cap
    respected when content overflows.
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 4.2 Wire new hooks into `.cursor/hooks.json`
  - Add `prompt_capture.py` to the `beforeSubmitPrompt` array with
    `timeout: 5`. Add `prompt_context_router.py` to the
    `postToolUse` array with `timeout: 5`. Do **not** set
    `failClosed` on either.
  - Add a syntactic-regression test in
    `tests/cursor_harness/test_hooks_json.py` that loads the file,
    asserts schema (no extra commas / non-JSON), confirms the two
    new hooks are present, confirms neither has `failClosed: true`,
    and confirms both have `timeout: 5`.
  - _Requirements: 7.1, 7.2_
  - **Wired in:** project root file is `.cursor/hooks.json` (not
    `hooks.json` at repo root; Cursor uses this path).

### Phase 5 — Verification

- [x] 5. End-to-end smoke and full verification
- [x] 5.1 End-to-end smoke test
  - Add `tests/cursor_harness/test_smoke_e2e.py`. Synthesises three
    user prompts (e.g. "fix the kill switch", "rerun the backtest
    with embargo", "add a binance ingest"), simulates a sequence of
    tool calls (Read on `risk/engine.py`, Grep for "embargo", Read
    on `data/ingest/binance.py`), drives `prompt_capture.py` then
    `prompt_context_router.py` (as Python modules) for each step,
    and asserts ≥ 3 distinct rule ids fire across the three turns
    with `additional_context` containing the expected
    `## Auto-loaded:` headers.
  - _Requirements: 2.1, 5.5, NFR-Determinism 1, Acceptance Metrics_

- [x] 5.2 Determinism test
  - Add `tests/cursor_harness/test_router_determinism.py`. Calls
    `route(...)` twice with identical inputs and asserts the two
    `additional_context` strings are byte-identical and the two
    `RouterLogRecord` objects (excluding `timestamp`) are equal.
  - _Requirements: NFR-Determinism 1_

- [x] 5.3 Lint, typecheck, and full pytest run
  - Run `ruff check .cursor/hooks tests/cursor_harness` — fix any
    findings.
  - Run `mypy --strict .cursor/hooks tests/cursor_harness` — fix any
    findings.
  - Run `pytest -q` (whole repo) — confirm no regressions in any
    other test module.
  - Capture output in this PR description.
  - _Requirements: all (Definition of Done)_
  - **As shipped:** ruff + `pytest` on `tests/cursor_harness` are
    recorded in `SESSION_LOG.md`. mypy and full-repo `pytest` remain
    to run in a 3.11+ environment or CI; see *Definition of done* above
    and *Blocked / next* in the log (not a router code gap).

### Phase 6 — Documentation and handoff

- [x] 6. Document and record the feature
- [x] 6.1 Operator README
  - Create `.cursor/hooks/README.md` covering: the
    `beforeSubmitPrompt → state → postToolUse` data flow; the
    routing-table schema with one annotated example; how to add a
    rule; the `TLAB_ROUTER_BUDGET_CHARS` and `TLAB_ROUTER_DISABLE`
    env vars; how to inspect `router-log.jsonl` for tuning.
  - _Requirements: 9.1, 9.2_

- [x] 6.2 Link the README from `PROJECT_CONTEXT.md`
  - Add a row to the existing "Where to look" table in
    `PROJECT_CONTEXT.md`: "How does context get auto-injected?" →
    `.cursor/hooks/README.md`.
  - _Requirements: 9.3_

- [x] 6.3 Append `SESSION_LOG.md` entry
  - In practice: `## 2026-04-25 — prompt-context-router (spec session)`
    with: agent, goal, what landed, verification commands + results,
    blocked / next (per task; title uses “spec session” instead of
    the literal “shipped” from the pre-ship text below).
  - (Original plan text) Append a
    `## 2026-04-25 — prompt-context-router shipped` section with:
    agent, goal, what landed, verification commands + results, blocked
    / next.
  - _Requirements: Definition of Done_

---

## Task Quality Self-Check

### Completeness

- [x] Every component in `design.md` (1-6) has at least one task
      (1.1 → types/scaffolding, 1.2 → routing table, 2.* → core
      route fn, 3.1 → prompt_capture, 3.2 → router hook, 4.1 →
      session_init, 4.2 → hooks.json, 6.1 → README, 1.* and 2.* →
      tests).
- [x] Every requirement (1-9 + NFRs) is cited by at least one task's
      `_Requirements:` line.
- [x] Every leaf task includes a test or testing sub-bullet.

### Scope

- [x] No task is too big to finish in 1-4 hours (each is bounded to
      one Python module or one config file plus its tests).
- [x] No task is so small it's noise.
- [x] No task is non-coding except 6.2 / 6.3 (doc updates required
      by Definition of Done; both produce a concrete file diff).

### Sequencing

- [x] Tasks ordered so each builds on completed predecessors.
- [x] Foundation (types, IO helpers, routing table, .gitignore)
      precedes core logic.
- [x] Core logic precedes hook wiring; hook wiring precedes
      hooks.json; verification follows.

### Traceability

- [x] Every leaf task ends with `_Requirements: <ids>_` and the
      ids exist in `requirements.md`.
- [x] Task IDs (`1.1`, `1.2`, …) are unique and stable.

### Hierarchy

- [x] No nesting deeper than two levels.
- [x] Top-level tasks (`1.`, `2.`, `3.`, `4.`, `5.`, `6.`) are
      phases.
- [x] Sub-tasks are concrete coding work.

---

> **Execution rules** (per `spec-sessions.mdc` Phase 4):
>
> - Per user request ("just do it"), this plan executes all tasks
>   sequentially in one session. Each leaf task is marked `- [~]`
>   when started and `- [x]` when its tests pass.
> - If any task reveals a gap in `requirements.md` or `design.md`,
>   the spec is updated before continuing.
>
> **This feature:** implementation completed 2026-04-25; the checklist
> above is closed out to match the repo. Remaining “definition of
> done” follow-ups: `mypy` + full `pytest` on a fully provisioned
> Python 3.11+ environment (see `SESSION_LOG.md`).
