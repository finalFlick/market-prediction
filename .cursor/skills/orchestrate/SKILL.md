---
name: orchestrate
description: Run the continuous agent work loop for trading-lab — plan, dispatch to domain subagents, collect, verify, repeat. Use this skill when the user asks to orchestrate, drive, or coordinate work that spans multiple pipeline stages.
---

# orchestrate

Project-tuned variant of the user-level `orchestrate` skill. This one
knows about the trading-lab pipeline, the domain subagents in
`.cursor/agents/`, and the gates that block promotion.

## When to use

- A task spans more than one pipeline stage (e.g. "ingest BTC, train a
  model, backtest it, evaluate it").
- The user says "orchestrate", "drive this end-to-end", "manage the loop".

## The loop

```
plan  →  dispatch  →  collect  →  verify  →  repeat
                                       ↓
                                 release-gate
```

1. **Plan.** Switch to plan mode (or write a plan inline). Use
   [`session-init`](mdc:.cursor/skills/session-init/SKILL.md) to load
   context, then break the goal into pipeline-stage-aligned tasks.
2. **Dispatch.** For each task, choose the right subagent:

   | Task                                | Subagent                                      |
   |-------------------------------------|-----------------------------------------------|
   | Discover signal from a paper        | `.cursor/agents/research.md`                  |
   | Implement feature / model           | `.cursor/agents/signal.md`                    |
   | Compose strategy                    | `.cursor/agents/strategy.md`                  |
   | Run a backtest                      | `.cursor/agents/backtest.md`                  |
   | Approve a promotion                 | `.cursor/agents/risk.md` (readonly)           |
   | Score against gates                 | `.cursor/agents/evaluation.md` (readonly)     |
   | Watch for drift after deploy        | `.cursor/agents/monitoring.md` (readonly)     |
   | Propose a new rule from observed signal | `.cursor/agents/reviewer.md` (readonly)   |
   | Pure exploration                    | built-in `explore`                            |
   | Single isolated implementation      | built-in `developer`                          |

3. **Collect.** Read each subagent's summary. Do not paper over failures.
4. **Verify.** Run `pytest -q`, `ruff check .`, `mypy --strict ...`. For
   strategy work, run `pytest tests/strategy -q` and the backtest smoke.
5. **Release gate.** Before declaring done, check
   [`workflow.mdc`](mdc:.cursor/rules/workflow.mdc) "definition of done".

## Outputs

- A markdown plan posted in the response.
- One subagent task per stage; their summaries collected.
- A green test run cited verbatim.
- A `SESSION_LOG.md` entry written by the `append_session_log` hook.

## Forbidden

- Marking the loop done while any verification step is red.
- Dispatching `developer` for risk/execution work — use the project's
  `risk` and `evaluation` readonly agents to gate first.
- Running parallel subagents that share the same files (race risk).
