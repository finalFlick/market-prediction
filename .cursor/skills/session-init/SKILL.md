---
name: session-init
description: Orient at session start by reading PROJECT_CONTEXT.md, the last 5 SESSION_LOG entries, and any pending proposals. Use this skill at the start of every non-trivial trading-lab session before doing other work.
---

# session-init

This skill should be used at the start of every trading-lab session to
load the project's operating manual into the agent's context before
making changes.

## When to use

- The user opens a fresh session with a non-trivial task.
- The agent is uncertain about the project's pipeline, conventions, or
  recent decisions.
- The `sessionStart` hook (`.cursor/hooks/session_init.py`) has already
  injected base context but the task is large enough to benefit from
  re-reading the operating docs.

## Procedure

1. Read [`PROJECT_CONTEXT.md`](mdc:PROJECT_CONTEXT.md) (top-level entry doc).
2. Read [`AGENTS.md`](mdc:AGENTS.md) for ownership of the relevant pipeline
   stage, then the matching `.cursor/agents/<name>.md` if a domain agent exists.
3. Read the **last five entries** of `SESSION_LOG.md` (tail) to understand
   what was just done and what's in flight.
4. Read `DECISIONS.md` tail (last 3 entries) to learn recent architectural
   decisions you must respect.
5. If `.cursor/state/proposed/` exists and has unreviewed entries, read
   them and surface them to the user — do not silently apply.
6. For the specific task, also read the matching MDC rule under
   `.cursor/rules/` (e.g. for backend work, `backend.mdc`; for risk work,
   `risk-management.mdc`).

## Outputs

- A 3-5 bullet "what I just learned" summary in the agent response.
- A clear restatement of the task with constraints from the rules.
- Acceptance criteria for "done" before any edits begin.

## Forbidden

- Skipping this skill on a multi-file change. The
  [`workflow.mdc`](mdc:.cursor/rules/workflow.mdc) rule requires plan-first
  for multi-file work, and that requires this orientation.
