# `.cursor/hooks/` — operator notes

This directory holds the project's Cursor hook scripts. They observe
and shape the agent loop. Cursor calls each script as a subprocess
with JSON on stdin and expects JSON on stdout. The wiring lives in
`.cursor/hooks.json`.

This README focuses on the **prompt-context-router**, the most
recently added subsystem. Other hooks (formatters, guards, loggers)
are self-explanatory; their inline docstrings cover them.

## Prompt-context-router at a glance

Goal: inject **targeted excerpts of steering files** (`docs/`,
`.cursor/rules/`, `.cursor/agents/`, `.cursor/skills/`) into the
agent's context the moment a topic becomes relevant — without
bloating the always-on rule set.

```
User submits a prompt
        │
        ▼
beforeSubmitPrompt:  prompt_capture.py
        │  writes redacted prompt + session_id
        ▼
   .cursor/state/last-prompt.json   (gitignored, mtime-aged)
        │
        ▼
Agent runs a tool (Read / Grep / Shell / Write / ...)
        │
        ▼
postToolUse:        prompt_context_router.py
        │  reads last-prompt.json + tool input/output
        │  matches against .cursor/context-router.json
        │  dedups against .cursor/state/session-context-memory.json
        │  enforces per-turn char budget
        │  appends a JSONL audit line to .cursor/state/router-log.jsonl
        ▼
   stdout: {"additional_context": "## Auto-loaded: docs/RISK_POLICY.md ..."}
```

`additional_context` from `postToolUse` is injected after the tool
result, per the [Cursor hook docs](https://cursor.com/docs/agent/hooks).

## Files

| File | Role |
|---|---|
| `prompt_capture.py` | `beforeSubmitPrompt` hook — observation only, never blocks |
| `prompt_context_router.py` | `postToolUse` hook — does the actual context injection |
| `_router_types.py` | `TypedDict` schemas (`mypy --strict`-friendly) |
| `_router_io.py` | atomic JSON / JSONL helpers |
| `_router_core.py` | pure routing functions: load, match, excerpt, prune, route |
| `../context-router.json` | committed routing table (the data) |
| `../state/last-prompt.json` | runtime: latest prompt (gitignored) |
| `../state/session-context-memory.json` | runtime: per-session dedupe (gitignored) |
| `../state/router-log.jsonl` | runtime: audit log capped at 5000 lines (gitignored) |

## Routing-table schema

`/.cursor/context-router.json`:

```json
{
  "version": 1,
  "rules": [
    {
      "id": "risk-policy",
      "priority": 100,
      "description": "Risk policy and the non-bypassable risk engine.",
      "match": {
        "prompt_regex": ["(?i)\\bkill[- ]?switch\\b", "(?i)\\brisk\\b"],
        "tool_input_regex": ["risk[\\\\/]engine\\.py"],
        "tool_output_regex": ["..."],
        "agent_message_regex": ["..."],
        "tool_name_in": ["Read", "Grep", "Write", "StrReplace"]
      },
      "snippets": [
        { "path": "docs/RISK_POLICY.md", "anchor": null, "max_chars": 1200 },
        { "path": ".cursor/rules/risk-management.mdc", "anchor": "## Limits", "max_chars": 600 }
      ]
    }
  ]
}
```

**Match semantics.** Trigger keys are OR-combined: a rule may fire when any
of `prompt_regex`, `tool_input_regex`, `tool_output_regex`, or
`agent_message_regex` matches. Inside any list-valued key, any element matches
(logical OR). `tool_name_in` is an additional AND filter when present. A rule
with an empty `match` never fires.

**Snippet semantics.**

- `anchor: null` → reads the head of the file.
- `anchor: "## Limits"` → reads from that header to the next `## `
  header (exclusive) or EOF.
- `max_chars` caps the excerpt; over-budget snippets are truncated
  with a trailing `\n\n... [truncated]` marker.

**Path safety.** Paths are validated to be repo-relative; absolute
paths and traversal (`..`) are rejected at load time.

**Priority.** Higher `priority` wins when the per-turn budget runs
out. Defaults to 0 if missing.

## Adding a rule

1. Open `/.cursor/context-router.json`.
2. Append a new entry to `rules`. Pick an `id` not already used.
3. Choose a sensible `priority` (existing rules range 40-100).
4. Write your `match` patterns. Test them locally with `python
   -c 'import re; print(re.search(r"PATTERN", "test text"))'`.
5. List the snippets to inject. Keep `max_chars` proportional to
   how often the rule will fire — under-cap, not over.
6. Run the routing-table sanity test:
   `pytest -q tests/cursor_harness/test_routing_table.py`.
7. Commit. The router picks up the change on the next hook
   invocation; no restart needed.

## Env-var overrides

| Env var | Type | Default | Effect |
|---|---|---|---|
| `TLAB_ROUTER_DISABLE` | truthy string | unset | Both new hooks short-circuit and emit safe output. Use as a kill switch when debugging. |
| `TLAB_ROUTER_BUDGET_CHARS` | integer | `3000` | Override the per-turn `additional_context` char budget. |

## Inspecting behaviour

`/.cursor/state/router-log.jsonl` holds one record per turn:

```json
{
  "timestamp": "2026-04-25T18:00:00.000+00:00",
  "session_id": "abc123",
  "tool_name": "Read",
  "matched_rule_ids": ["risk-policy"],
  "injected_snippets": [{"path": "docs/RISK_POLICY.md", "anchor": null, "chars": 1247}],
  "total_chars": 1247,
  "skip_reason": null
}
```

Useful one-liners:

```powershell
# Which rules fire most?
Get-Content .cursor/state/router-log.jsonl | ConvertFrom-Json |
  ForEach-Object { $_.matched_rule_ids } | Group-Object | Sort-Object Count -Desc

# Most-injected snippets
Get-Content .cursor/state/router-log.jsonl | ConvertFrom-Json |
  ForEach-Object { $_.injected_snippets.path } | Group-Object | Sort-Object Count -Desc
```

## Disabling temporarily

```powershell
$env:TLAB_ROUTER_DISABLE = "1"   # current shell only
```

To remove permanently, drop the two new entries from
`.cursor/hooks.json` (`beforeSubmitPrompt` and `postToolUse` blocks).
The hooks fail-open — leaving them broken does not break sessions —
but it's tidier to remove them.

## Failure modes (all fail-open)

| Failure | Behaviour |
|---|---|
| Routing table missing or malformed | warning to stderr; emit `{}` |
| Bad regex in a rule | drop that rule on load; remaining rules still fire |
| Snippet file missing | skip that snippet; other snippets still inject |
| State file unreadable | recreate it; treat session as empty |
| Hook crashes with unhandled exception | top-level `except BaseException`: log to stderr, emit safe output, exit 0 |
| Hook exceeds `timeout: 5` | Cursor kills it; treated as fail-open |

## Operational lesson

Hooks, skills, and routed context are not a substitute for explicit verification.
After changing this harness, run `pytest tests/cursor_harness -q`. If a skill or
rule should have triggered but did not, manually read the relevant `SKILL.md` or
`.mdc` file and update routing/rules only when the improvement is durable.

## See also

- `specs/prompt-context-router/` — full spec (requirements, design, tasks).
- [Cursor hooks docs](https://cursor.com/docs/agent/hooks) —
  authoritative event list and JSON contracts.
- `.cursor/rules/spec-sessions.mdc` — Kiro spec workflow this
  feature was built under.
