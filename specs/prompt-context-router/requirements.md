# Requirements: prompt-context-router

## Document Information

- **Feature Name**: prompt-context-router
- **Version**: 0.1
- **Date**: 2026-04-25
- **Author**: Brandon
- **Stakeholders**: trading-lab maintainers, AI agents working in `.cursor/`
- **Related Documents**:
  - Design: `./design.md`
  - Tasks: `./tasks.md`
  - Cursor hooks reference: <https://cursor.com/docs/agent/hooks>
  - `.cursor/rules/spec-sessions.mdc`
  - `.cursor/hooks/session_init.py` (existing sessionStart context loader)
  - `.cursor/hooks/spec-session-init.js` (existing spec status loader)

## Introduction

Cursor agent chats in trading-lab today receive a one-shot orientation at
session start (`session_init.py` injects `PROJECT_CONTEXT.md`, the last 5
`SESSION_LOG.md` entries, and any pending proposals; `spec-session-init.js`
adds the spec workflow reminder). Always-on rules under `.cursor/rules/`
with `alwaysApply: true` and glob-scoped rules also load. However, **no
mechanism injects relevant context mid-conversation based on what the
user is asking or what the agent is doing**. Important steering material
in `docs/` (e.g. `RISK_POLICY.md`, `EVALUATION.md`, `DATA_MODEL.md`,
`INFRASTRUCTURE.md`) is referenced from `PROJECT_CONTEXT.md` but never
auto-loaded; agents must remember to read it.

This feature adds a **prompt-context-router**: a small, data-driven
system that observes user prompts and agent tool use, and injects
targeted snippets from `docs/`, `.cursor/rules/`, `.cursor/agents/`, or
`.cursor/skills/` into the conversation when their topic becomes
relevant. It uses Cursor's `postToolUse` hook for injection (the only
per-turn hook that supports `additional_context` per the official
docs), backed by a `beforeSubmitPrompt` hook that records the user's
latest prompt to disk so behavioural and prompt-derived signals can
combine.

### Feature Summary

A per-session, data-driven router that injects targeted excerpts of
trading-lab steering files into the agent's context based on the user's
prompt and the agent's recent tool use, with deduplication and a
hard char budget.

### Business Value

- Cuts the rate at which agents violate documented conventions (no
  look-ahead, non-bypassable risk, LLM isolation) by surfacing the
  matching rule/doc the moment the relevant topic comes up.
- Reduces wasted tool calls spent rediscovering things already
  documented in `docs/` or `.cursor/agents/`.
- Makes the steering-file investment under `docs/` and `.cursor/`
  pay off without bloating the always-on rule set.

### Scope

- **In scope:**
  - A `beforeSubmitPrompt` hook (`prompt_capture.py`) that observes
    the user's prompt and persists it to a per-session state file.
    Always returns `{ "continue": true }` — never blocks.
  - A `postToolUse` hook (`prompt_context_router.py`) that reads the
    latest captured prompt + the current tool call, matches against a
    routing table, and emits `additional_context`.
  - A JSON routing table at `.cursor/state/context-router.json`
    mapping prompt regex / tool-input regex / file-path glob → list of
    snippets to inject (file path + section anchor + per-snippet
    char budget).
  - Per-session deduplication memory at
    `.cursor/state/session-context-memory.json` keyed by `session_id`.
  - A per-turn hard char budget (default 3000 chars) enforced by the
    router.
  - Augmentation of `session_init.py` to also emit a one-line **doc
    map** (titles + paths of every steering file) so the agent knows
    what is available to request.
  - Augmentation of `session_init.py` to mention the `session-init`
    skill so the agent invokes it on multi-file tasks.
  - Wiring of both new hooks into `.cursor/hooks.json`.
  - A pytest unit-test module under `tests/cursor_harness/` exercising
    the router's matching, deduplication, budgeting, and fail-open
    behaviour offline (the hooks themselves are pure-stdin/stdout
    Python, so they are unit-testable without Cursor).
  - A short operator doc at `.cursor/hooks/README.md` explaining the
    router and how to extend the routing table.

- **Out of scope:**
  - Replacing the existing `session_init.py` — we only augment it.
  - Replacing always-on `.cursor/rules/*.mdc` — those stay as-is.
  - Any LLM-driven routing (this v1 is purely deterministic regex /
    glob matching). LLM-based routing would have to honour
    `.cursor/rules/llm-usage.mdc` and is deferred.
  - Routing for Tab completions (`beforeTabFileRead`,
    `afterTabFileEdit`) — out of scope; this is for Agent chats.
  - Cross-session memory beyond the current session id.

---

## Requirements

### Requirement 1: Capture user prompt for downstream routing

**User Story:** As a trading-lab maintainer, I want every user prompt
recorded to a known location, so that the post-tool router can use the
prompt as one of its routing signals even though `beforeSubmitPrompt`
itself cannot inject context.

#### Acceptance Criteria

1. WHEN the user submits a prompt in an Agent chat THE SYSTEM SHALL
   write a JSON record to `.cursor/state/last-prompt.json` containing
   `session_id`, `prompt`, `attachments`, and an ISO-8601 `captured_at`
   timestamp.
2. THE SYSTEM SHALL return `{ "continue": true }` from
   `beforeSubmitPrompt` regardless of prompt content. THE SYSTEM SHALL
   NOT block submission.
3. IF writing the state file fails THEN THE SYSTEM SHALL still return
   `{ "continue": true }` and log a single line to stderr.
4. THE SYSTEM SHALL redact obvious secret-like substrings (using the
   existing `_common.redact` helper) from the persisted prompt before
   writing.
5. THE SYSTEM SHALL truncate the persisted prompt to at most 8000
   characters.
6. WHERE the input JSON does not include a `session_id` THE SYSTEM
   SHALL use `"unknown"` as the session id rather than crashing.

#### Additional Details

- **Priority:** High
- **Complexity:** Low
- **Dependencies:** existing `.cursor/hooks/_common.py` helpers.
- **Assumptions:** Cursor passes a stable `session_id` across the
  hooks of a single chat; the docs do not guarantee this for
  `beforeSubmitPrompt`, so the router degrades to mtime-based
  freshness checks if `session_id` is missing.

---

### Requirement 2: Route context after tool use

**User Story:** As a trading-lab maintainer, I want the router to inject
the most relevant steering file snippets into the agent's context when
the user's question or the agent's behaviour matches a known topic, so
the agent stops re-discovering documented conventions.

#### Acceptance Criteria

1. WHEN the `postToolUse` hook fires THE SYSTEM SHALL read both
   `.cursor/state/last-prompt.json` (if its `captured_at` is within the
   last 30 minutes) and the hook input (`tool_name`, `tool_input`,
   `tool_output`).
2. WHEN any rule in the routing table matches the prompt or the tool
   input/output THE SYSTEM SHALL emit a non-empty `additional_context`
   string composed of the rule's snippet excerpts.
3. IF no rule matches THEN THE SYSTEM SHALL return an empty JSON
   object `{}` (i.e. inject nothing).
4. THE SYSTEM SHALL prepend each injected snippet with a header of the
   form `## Auto-loaded: <relative_path><#anchor> (rule: <rule_id>)`
   so the agent can see the source.
5. THE SYSTEM SHALL load the routing table from
   `.cursor/state/context-router.json` on every invocation. IF the
   file is missing or malformed THEN THE SYSTEM SHALL emit `{}` and
   log a single warning line to stderr.
6. WHERE a routing rule cites a file that does not exist THE SYSTEM
   SHALL skip that rule and continue with remaining rules.

#### Additional Details

- **Priority:** High
- **Complexity:** Medium
- **Dependencies:** Requirement 1 (prompt state file), the v1 routing
  table (Requirement 5).
- **Assumptions:** `additional_context` returned from `postToolUse` is
  injected after the tool result, per the documented schema.

---

### Requirement 3: Deduplicate within a session

**User Story:** As an AI agent in a long chat, I want each steering
snippet injected at most once per session unless something changes,
so my context window is not flooded with the same `RISK_POLICY.md`
header on every turn.

#### Acceptance Criteria

1. THE SYSTEM SHALL maintain a per-session memory file at
   `.cursor/state/session-context-memory.json` containing, for each
   `session_id`, the set of `(rule_id, snippet_path, anchor)` triples
   already injected.
2. WHEN a routing rule matches and its `(rule_id, path, anchor)` is
   already in this session's memory THE SYSTEM SHALL skip that
   snippet.
3. IF the routing-table entry for a rule has been edited since the
   last injection (detected by sha256 hash of the snippet text in the
   memory record) THEN THE SYSTEM SHALL re-inject the snippet and
   update the memory.
4. THE SYSTEM SHALL prune session-memory entries older than 24 hours
   on each invocation to bound the file size.
5. WHERE the memory file is missing or unreadable THE SYSTEM SHALL
   treat the session as having no prior injections (fail-open) and
   recreate the file.

#### Additional Details

- **Priority:** High
- **Complexity:** Medium
- **Dependencies:** Requirement 2.

---

### Requirement 4: Enforce a per-turn context budget

**User Story:** As a trading-lab maintainer, I want a hard char budget
on injected context per turn, so the router cannot blow out the agent's
context window even with a permissive routing table.

#### Acceptance Criteria

1. THE SYSTEM SHALL apply a per-turn budget defaulting to 3000
   characters across all `additional_context` injected by a single
   `postToolUse` invocation.
2. WHEN the cumulative size of selected snippets would exceed the
   budget THE SYSTEM SHALL drop the lowest-priority snippets first
   (priority comes from the routing table).
3. WHERE a single snippet is larger than the per-snippet
   `max_chars` declared in the routing table THE SYSTEM SHALL
   truncate it and append a single line `... [truncated]`.
4. IF the budget cannot fit even the highest-priority matched
   snippet (e.g. budget is set absurdly low) THEN THE SYSTEM SHALL
   inject nothing and log a stderr warning naming the dropped rule.
5. THE SYSTEM SHALL allow the per-turn budget to be overridden by
   the env var `TLAB_ROUTER_BUDGET_CHARS` (integer, characters) for
   debugging.

#### Additional Details

- **Priority:** High
- **Complexity:** Low
- **Dependencies:** Requirement 2.

---

### Requirement 5: Data-driven routing table

**User Story:** As a trading-lab maintainer, I want routing rules
defined in JSON, so I can add a new topic without editing Python code.

#### Acceptance Criteria

1. THE SYSTEM SHALL load routing rules from
   `.cursor/state/context-router.json`. THE SYSTEM SHALL NOT hardcode
   any rule in Python.
2. THE SYSTEM SHALL accept a routing rule schema of the form (validated
   on load):

   ```json
   {
     "id": "risk-policy",
     "priority": 100,
     "match": {
       "prompt_regex": ["(?i)\\b(risk|kill[- ]?switch|position size|risk\\s*engine)\\b"],
       "tool_input_regex": ["risk/engine\\.py", "configs/risk\\.yaml"],
       "tool_name_in": ["Read", "Grep", "Write", "StrReplace"]
     },
     "snippets": [
       {
         "path": "docs/RISK_POLICY.md",
         "anchor": null,
         "max_chars": 1200
       },
       {
         "path": ".cursor/rules/risk-management.mdc",
         "anchor": null,
         "max_chars": 800
       }
     ]
   }
   ```

3. WHEN any present trigger key on a rule matches its target THE
   SYSTEM SHALL consider the rule triggered. Trigger keys
   (`prompt_regex`, `tool_input_regex`, `tool_output_regex`,
   `agent_message_regex`) are **OR-combined** across keys; entries
   within any single list-valued key are **OR-combined** as well.
   `tool_name_in` is a filter (AND-ed with the trigger result):
   when present the current tool name must appear in the list.
4. IF the routing-table file fails JSON parse OR fails schema
   validation THEN THE SYSTEM SHALL inject nothing, log a stderr
   warning, and continue (fail-open).
5. THE SYSTEM SHALL ship a v1 routing table with at minimum these
   eight rule ids: `risk-policy`, `evaluation-gates`,
   `signal-research`, `data-ingest`, `frontend-dashboard`,
   `infra-deployment`, `llm-isolation`, `spec-workflow`.

#### Additional Details

- **Priority:** High
- **Complexity:** Medium
- **Dependencies:** Requirement 2, Requirement 4.

---

### Requirement 6: Augmented session-start orientation

**User Story:** As an AI agent starting a fresh chat, I want a one-line
doc map of every steering file plus a pointer to the `session-init`
skill, so I know what context is available without reading
`PROJECT_CONTEXT.md` cover-to-cover.

#### Acceptance Criteria

1. WHEN `session_init.py` runs THE SYSTEM SHALL append a section
   titled `## Steering files (read on demand)` listing every
   markdown file under `docs/` and `.cursor/agents/` with a
   one-line title (first H1 of the file, fallback to filename).
2. WHEN `session_init.py` runs THE SYSTEM SHALL append a section
   titled `## How to invoke` with a single bullet referencing the
   `session-init` skill at
   `.cursor/skills/session-init/SKILL.md`.
3. THE SYSTEM SHALL keep the total `additional_context` from
   `session_init.py` under 8000 characters (raised from the current
   6000 to fit the doc map).
4. IF a file under `docs/` or `.cursor/agents/` cannot be read THEN
   THE SYSTEM SHALL still emit the rest of the doc map.

#### Additional Details

- **Priority:** Medium
- **Complexity:** Low
- **Dependencies:** none.

---

### Requirement 7: Fail-open and bounded execution

**User Story:** As a trading-lab maintainer, I want the new hooks to
never break a chat session, so an experiment in the routing table can
never lock me out of my own agent.

#### Acceptance Criteria

1. THE SYSTEM SHALL configure both new hooks in `hooks.json` without
   `failClosed: true`. Hook crashes SHALL NOT block any agent action.
2. THE SYSTEM SHALL configure both new hooks with an explicit
   `timeout: 5` (seconds) in `hooks.json`.
3. WHEN any unhandled exception is raised inside a hook THE SYSTEM
   SHALL catch it, log a single line to stderr, write `{}` to stdout,
   and exit with code 0.
4. THE SYSTEM SHALL never write outside `.cursor/state/` and the
   project's `SESSION_LOG.md` from these hooks. THE SYSTEM SHALL NOT
   call any network endpoint.
5. THE SYSTEM SHALL have zero third-party imports; only the Python
   stdlib + `_common.py` helpers.

#### Additional Details

- **Priority:** High
- **Complexity:** Low
- **Dependencies:** none.

---

### Requirement 8: Observability of routing decisions

**User Story:** As a trading-lab maintainer, I want a record of which
rules fired and which snippets were injected per turn, so I can tune
the routing table empirically.

#### Acceptance Criteria

1. WHEN the router injects context THE SYSTEM SHALL append a JSONL
   record to `.cursor/state/router-log.jsonl` with fields:
   `timestamp`, `session_id`, `tool_name`, `matched_rule_ids`,
   `injected_snippets` (list of `{path, anchor, chars}`), and
   `total_chars`.
2. WHEN the router skips a matched rule due to deduplication THE
   SYSTEM SHALL still record it with `injected_snippets: []` and a
   `skip_reason: "deduplicated"` field.
3. THE SYSTEM SHALL truncate the JSONL log to its last 5000 lines on
   every invocation to bound disk usage.
4. THE SYSTEM SHALL NOT log raw prompt text or tool input; only
   matched rule ids and snippet paths.

#### Additional Details

- **Priority:** Medium
- **Complexity:** Low
- **Dependencies:** Requirements 2-4.

---

### Requirement 9: Operator documentation

**User Story:** As a future contributor, I want a short README that
explains the router so I can extend the table without reading every
hook script.

#### Acceptance Criteria

1. THE SYSTEM SHALL ship `.cursor/hooks/README.md` documenting:
   - the data flow `beforeSubmitPrompt → state → postToolUse`,
   - the routing-table schema,
   - how to add a new rule,
   - the env-var overrides (`TLAB_ROUTER_BUDGET_CHARS`,
     `TLAB_ROUTER_DISABLE`).
2. THE SYSTEM SHALL document the `TLAB_ROUTER_DISABLE` env var which,
   when set to a truthy value, makes both new hooks return immediately
   with `{}`.
3. THE SYSTEM SHALL reference this README from `PROJECT_CONTEXT.md`
   under the existing "Where to look" table.

#### Additional Details

- **Priority:** Medium
- **Complexity:** Low

---

## Non-Functional Requirements

### Performance

1. WHEN `prompt_capture.py` runs THE SYSTEM SHALL complete in under
   100 ms p95 measured locally on Windows + Python 3.11.
2. WHEN `prompt_context_router.py` runs THE SYSTEM SHALL complete in
   under 200 ms p95 with a routing table of up to 50 rules.
3. WHEN any hook exceeds its 5 s `timeout` Cursor will kill it; THE
   SYSTEM SHALL design the inner loop to finish well below this,
   targeting a 300 ms p99.

### Reliability

1. IF any state file (last-prompt, session-memory, router-log) is
   corrupt THEN THE SYSTEM SHALL recreate it and continue.
2. WHEN two hook invocations race on the memory or log file THE
   SYSTEM SHALL tolerate the race (best-effort writes; small lost
   updates are acceptable). THE SYSTEM SHALL NOT corrupt the file.

### Security

1. THE SYSTEM SHALL NOT log raw user prompts to disk except for the
   transient `last-prompt.json` (which lives only under
   `.cursor/state/`, is gitignored, and is overwritten on each
   prompt).
2. THE SYSTEM SHALL run `_common.redact` on the persisted prompt to
   remove obvious secret-like fragments before writing.
3. THE SYSTEM SHALL respect `.cursor/rules/llm-usage.mdc`: the
   router SHALL NOT call any LLM, SHALL NOT import
   `research.llm.*`, and SHALL NOT inject snippets that reside under
   `execution/`.
4. THE SYSTEM SHALL respect `.cursor/rules/security.mdc`: the
   router SHALL NOT touch `risk/`, `execution/`, or `configs/`
   files at runtime.

### Observability

1. WHEN any hook emits `additional_context` THE SYSTEM SHALL also
   write a corresponding line to `.cursor/state/router-log.jsonl`.
2. WHEN any hook silently swallows an exception THE SYSTEM SHALL
   write a stderr line of the form `[router] <hook>: <exception>`.

### Determinism

1. WHEN given identical inputs (prompt, tool_input, routing table,
   session memory state) THE SYSTEM SHALL produce identical
   `additional_context` output.

### Maintainability

1. WHEN a new rule is added to `.cursor/state/context-router.json`
   THE SYSTEM SHALL pick it up on the next hook invocation; no
   restart required.
2. THE SYSTEM SHALL keep router code under 400 lines of Python
   total (excluding tests) — this feature is glue, not a framework.

---

## Constraints and Assumptions

### Technical Constraints

- Python 3.11+, mypy --strict, ruff line length 100 (per
  `.cursor/rules/coding-standards.mdc`).
- Stdlib-only; no new third-party Python dependencies (per
  `.cursor/rules/architecture.mdc` and `security.mdc`).
- `.cursor/hooks/*.py` must be pure stdin/stdout JSON, fail-open by
  default, and runnable on Windows PowerShell where the project lives
  (no shebang reliance, no shell pipelines).
- Hooks must work for cloud agents too (project hooks load there per
  Cursor docs); this means no host-specific paths.
- Module imports must respect the existing one-way pipeline. The
  router lives entirely under `.cursor/` and `tests/cursor_harness/`;
  it does NOT live in any pipeline package.

### Business Constraints

- No third-party LLM API keys (per `llm-usage.mdc`). The router is
  deterministic regex/glob matching only.
- No changes to `risk/`, `execution/`, `configs/risk.yaml`, or any
  trading-path file — this is pure tooling.
- No new always-on rules. New context comes from the data-driven
  routing table, not from `.cursor/rules/*.mdc` with
  `alwaysApply: true`.

### Assumptions

- Cursor's `postToolUse` hook output `additional_context` is
  injected verbatim into the agent's context after the tool result
  (per official docs).
- Cursor passes a `session_id` to `beforeSubmitPrompt`; if not, the
  router degrades to mtime freshness on `last-prompt.json`.
- Most steering content the router will inject lives under
  `docs/`, `.cursor/rules/`, `.cursor/agents/`, and
  `.cursor/skills/`. None of it is secret.

---

## Success Criteria

### Definition of Done

- [ ] All acceptance criteria for Requirements 1-9 are met.
- [ ] All non-functional requirements are met.
- [ ] `pytest -q tests/cursor_harness` passes (new tests).
- [ ] `pytest -q` passes overall (no regressions).
- [ ] `ruff check .cursor/hooks tests/cursor_harness` is green.
- [ ] `mypy --strict .cursor/hooks tests/cursor_harness` is green.
- [ ] An end-to-end smoke run (described in `tasks.md`) shows
      `additional_context` appearing for at least three of the
      eight v1 rules.
- [ ] `SESSION_LOG.md` entry added for the work session.
- [ ] `PROJECT_CONTEXT.md` references the new
      `.cursor/hooks/README.md`.
- [ ] No `DECISIONS.md` entry needed (no architectural shift; tooling
      change only). If review disagrees, add one.

### Acceptance Metrics

- Router unit-test suite covers: prompt match, tool-input match,
  tool-name match, AND between match keys, dedup, budget overflow,
  malformed routing table, missing snippet file, hook timeout,
  fail-open on exception. Coverage of `prompt_context_router.py` is
  ≥ 90% lines.
- v1 routing table contains ≥ 8 rules; smoke run injects ≥ 3 of
  them across three synthesized turns.
- p95 router latency under 200 ms on a routing table of 50 rules
  (measured by a `pytest -m perf` benchmark).
- Total LOC for new Python under `.cursor/hooks/` ≤ 400.

---

## Glossary

| Term | Definition |
|---|---|
| Steering file | A markdown file under `docs/`, `.cursor/rules/`, `.cursor/agents/`, or `.cursor/skills/` that documents a project rule, design, agent role, or operating procedure. |
| Routing rule | An entry in `.cursor/state/context-router.json` mapping prompt/tool-call patterns to one or more snippets to inject. |
| Snippet | A bounded excerpt of a steering file (defined by file path + optional anchor + max_chars) injected into the agent's context. |
| Per-turn budget | The maximum cumulative `additional_context` size the router will emit from a single `postToolUse` invocation. |
| Session memory | Per-session record of which `(rule_id, snippet)` pairs have already been injected, used for deduplication. |

---

## Requirements Review Checklist

### Completeness

- [x] Every user story has role + functionality + benefit.
- [x] Every requirement has at least one EARS acceptance criterion.
- [x] Non-functional requirements covered (perf, reliability,
      security, observability, determinism, maintainability).
- [x] Success metrics are quantitative.

### EARS validity

- [x] Every criterion uses WHEN / IF / WHILE / WHERE or is ubiquitous.
- [x] Every criterion ends with `THE SYSTEM SHALL <verb>`.
- [x] No vague adjectives.

### Traceability

- [x] Requirements are numbered (`Requirement 1` … `Requirement 9`).
- [x] Acceptance criteria within each requirement are numbered
      (`1.1`, `1.2`, …).
- [x] Dependencies between requirements are explicit.

### Project alignment

- [x] Compatible with `.cursor/rules/architecture.mdc` (router is
      tooling under `.cursor/`, not in any pipeline package).
- [x] Compatible with `.cursor/rules/security.mdc` (no secrets, no
      network, no touching `risk/` / `execution/` / `configs/`).
- [x] Compatible with `.cursor/rules/llm-usage.mdc` (deterministic
      regex routing; no LLM call from router).
- [x] Compatible with `.cursor/rules/coding-standards.mdc` (Python
      3.11, typing, stdlib only).

---

> **Next phase:** when this document is approved, fill in
> `./design.md` from `.cursor/spec-templates/design-template.md`.
