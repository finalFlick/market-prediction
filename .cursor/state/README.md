# `.cursor/state/`

Auto-written by the hooks in [`../hooks/`](../hooks). Most of this folder
is gitignored noise; only `proposed/` is committed.

## Files

| File                        | Source hook                            | Committed? |
|-----------------------------|----------------------------------------|------------|
| `thoughts.jsonl`            | `record_thought.py` (afterAgentThought)| no         |
| `risk-touches.jsonl`        | `guard_risk_files.py` (read/edit)      | no         |
| `decisions-pending.md`      | `record_decisions.py` (stop)           | no         |
| `session-summary.json`      | `record_decisions.py` (stop)           | no         |
| `proposed/*.md`             | `reviewer` agent (manually invoked)    | **yes**    |

The `proposed/` directory is the audit trail for the self-improvement
loop: the `reviewer` agent (see
[`../agents/reviewer.md`](../agents/reviewer.md)) writes proposals here
based on patterns it observes in the gitignored logs. A human ratifies a
proposal by:

1. Editing the proposal file's `## Decision` block to mark it ratified.
2. Committing the actual change to `.cursor/rules/`, `.cursor/skills/`,
   or wherever the proposal targets.
3. Appending a one-line entry to `DECISIONS.md` referencing the proposal.

The `reviewer` agent **never** edits anything outside this directory.

## Reading the logs

```bash
# Last 20 thoughts
tail -n 20 .cursor/state/thoughts.jsonl | jq

# Touches to risk files in the last day
jq -c 'select(.ts > "<iso>")' .cursor/state/risk-touches.jsonl
```
