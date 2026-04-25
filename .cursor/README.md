# `.cursor/` — trading-lab AI harness

This is the project's Cursor harness: every file here is either
**Cursor-loaded** (Cursor reads it directly) or **convention** (project
docs / state, not auto-loaded). The README labels each so future you
isn't fooled.

## Layout

```
.cursor/
├─ rules/            Cursor-loaded · MDC rules with frontmatter
├─ skills/           Cursor-loaded · `.cursor/skills/<name>/SKILL.md`
├─ agents/           Cursor-loaded · custom subagent definitions
├─ hooks.json        Cursor-loaded · hook configuration
├─ hooks/            Cursor-loaded · Python hook scripts (stdin/stdout JSON)
├─ mcp.json          Cursor-loaded · MCP server registry
├─ state/            convention   · auto-written by hooks (mostly gitignored)
└─ README.md         convention   · this file
```

## Rules — `.cursor/rules/`

Frontmatter fields: `description` (≤ 15 words), `globs` (file-scope), `alwaysApply` (bool).
[Cursor docs](https://cursor.sh/docs/rules).

| File                    | Scope                          | Always-on?  |
|-------------------------|--------------------------------|-------------|
| `architecture.mdc`      | pipeline + module boundaries   | yes         |
| `coding-standards.mdc`  | `**/*.py`                      | no          |
| `backend.mdc`           | `backend/**/*.py`              | no          |
| `frontend.mdc`          | `frontend/**/*.{ts,tsx}`       | no          |
| `docker.mdc`            | `**/Dockerfile`, `compose*.yml`| no          |
| `testing.mdc`           | `tests/**`, `ai_evals/**`      | no          |
| `evaluation.mdc`        | `backtests/**`, `research/models/**` | no    |
| `risk-management.mdc`   | risk policy + forbidden flags  | yes         |
| `ai-workflow.mdc`       | agent delegation + DOD         | yes         |
| `workflow.mdc`          | dev loop (analyze→plan→test)   | yes         |
| `security.mdc`          | secrets, live capital, network | yes         |
| `deployment.mdc`        | container topology             | no          |
| `llm-usage.mdc`         | LLM allowed/forbidden uses     | no          |

## Skills — `.cursor/skills/<name>/SKILL.md`

Frontmatter fields: `name` (=folder name), `description`. Cursor invokes
a skill when the user request semantically matches its description.
[Cursor docs](https://www.trycursor.com/docs/context/skills).

| Skill              | Use when…                                       |
|--------------------|-------------------------------------------------|
| `session-init`     | starting a non-trivial session — orient first   |
| `research-signal`  | adding a new signal hypothesis                  |
| `run-backtest`     | running a backtest end-to-end with verification |
| `evaluate-strategy`| scoring a backtest against the gates            |
| `promote-strategy` | advancing `backtest → paper → live → retired`   |
| `docker-build`     | building / booting / triaging the docker stack  |
| `orchestrate`      | driving multi-stage pipeline work               |
| `review-local`     | quick local audit before commit / PR            |

## Custom subagents — `.cursor/agents/<name>.md`

Frontmatter: `name`, `description`, `model`, `readonly`, `is_background`.
[Cursor subagents docs](https://cursor.com/docs/subagents.md).

| Agent        | Read-only? | Owns…                                        |
|--------------|------------|----------------------------------------------|
| `planner`    | yes        | the written plan; never edits code           |
| `research`   | no         | `research/`, `SIGNALS.md`                    |
| `signal`     | no         | `research/features/`, `research/models/`     |
| `strategy`   | no         | `strategies/`                                |
| `backtest`   | no         | `backtests/` (configs read-only)             |
| `risk`       | yes        | promotion-approval verdict                   |
| `evaluation` | yes        | gate-scoring report                          |
| `monitoring` | yes        | drift report; recommends kill-switch         |
| `reviewer`   | yes        | self-improvement proposals (`state/proposed/`) |

The `risk`, `evaluation`, `monitoring`, and `reviewer` agents are **gates**, not editors. They produce verdicts and proposals; humans act on them.

## Hooks — `.cursor/hooks.json` + `.cursor/hooks/*.py`

[Cursor hooks docs](https://cursor.com/docs/hooks). All scripts are
Python 3.11+, stdlib-only, and safe-on-crash (each wraps `main()` in a
try/except so a bug never silently blocks the agent — except where
`failClosed: true` is intentional).

| Event                  | Script                      | failClosed | Purpose                                         |
|------------------------|-----------------------------|------------|-------------------------------------------------|
| `sessionStart`         | `session_init.py`           |            | Inject PROJECT_CONTEXT + recent SESSION_LOG     |
| `beforeShellExecution` | `block_dangerous_shell.py`  | **yes**    | Block `rm -rf /`, force pushes, risk-bypass flags |
| `beforeShellExecution` (matcher `git commit`) | `pre_commit_review.py` | | Fast secret/slop scan on staged diff |
| `beforeMCPExecution`   | `guard_mcp_writes.py`       | **yes**    | Ask for confirmation on GitHub writes; block live-trade tools |
| `beforeReadFile`       | `guard_risk_files.py`       |            | Log access to `risk/`, `execution/`, risk configs |
| `afterFileEdit`        | `format_python.py`          |            | Run `ruff format` on edited Python files        |
| `afterFileEdit`        | `guard_risk_files.py`       |            | Log edits to risk-critical paths                |
| `afterAgentResponse`   | `append_session_log.py`     |            | Append a one-line `[auto]` note to SESSION_LOG.md |
| `afterAgentThought`    | `record_thought.py`         |            | Persist (redacted) thinking blocks for the reviewer agent |
| `stop`                 | `record_decisions.py`       |            | Append candidate decision notes to `state/decisions-pending.md` |

## MCP — `.cursor/mcp.json`

Already populated. See [`docs/MCP.md`](../docs/MCP.md) for which tools are useful in trading-lab.

## State — `.cursor/state/` (mostly gitignored)

See [`state/README.md`](./state/README.md). The only committed subfolder
is `proposed/`, where the `reviewer` agent writes self-improvement
proposals for humans to ratify.

## Self-improvement contract (honest, not magic)

```
hooks  →  state/*.jsonl  →  reviewer agent reads  →  proposes to state/proposed/
                                                                    ↓
                                                   human ratifies + DECISIONS.md
                                                                    ↓
                                                   commits the actual rule/skill change
```

**No hook ever auto-edits `.cursor/rules/` or `.cursor/skills/`.** That's
deliberate: a self-modifying trading bot is not a feature, it's a
liability. Audit-trail-first, automation-second.

## What is NOT here, and why

| Folder you might expect       | Why it's not here                                      |
|-------------------------------|--------------------------------------------------------|
| `.cursor/plugins/`            | Cursor has no plugin system. MCP servers fill this role. |
| `.cursor/planning/`           | Plan mode is a runtime toggle, not a folder. See [`WORKFLOW.md`](../WORKFLOW.md). |
| `.cursor/security/`           | No project-level permissions config exists. Security is enforced via `failClosed: true` hooks + `.cursor/rules/security.mdc` + `.cursorignore`. |
| `.cursor/prompts/`            | Not auto-loaded. Runtime LLM prompts live in [`research/llm/prompts.py`](../research/llm/prompts.py); IDE-agent reasoning patterns live in `.cursor/skills/`. |

## Verifying the harness

```bash
# Lint every MDC rule (frontmatter parse)
python -c "import pathlib, re; [print(p) for p in pathlib.Path('.cursor/rules').glob('*.mdc')]"

# Smoke every hook against sample stdin
pytest tests/cursor_harness -q
```
