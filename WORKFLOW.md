# WORKFLOW

Every change — human or agent — follows this loop. A task is **not complete**
until step 6 passes. The full version lives in
[`.cursor/rules/workflow.mdc`](.cursor/rules/workflow.mdc).

## The loop

| Step | What                                  | Command(s)                                 |
|-----:|---------------------------------------|--------------------------------------------|
| 1    | Analyze the task                      | restate goal · constraints · acceptance    |
| 2    | Identify files to modify              | `git status`, `rg <symbol>`                |
| 3    | Implement the minimal change          | smallest possible diff, no drive-bys       |
| 4    | Run tests                             | `pytest -q`                                |
| 5    | Run lint + typecheck                  | `ruff check .` · `mypy --strict .`         |
| 6    | Validate the system end-to-end        | `pytest -q -m e2e` · `python -m backtests.smoke` |

If a task is too large for one PR, split it. Track sub-PRs in `TODO.md`.

## Definition of done

- [ ] Acceptance criteria met (with evidence: commands run + their results).
- [ ] `pytest`, `ruff`, `mypy` all green.
- [ ] At least one e2e or backtest smoke test exercises the new code path.
- [ ] `SESSION_LOG.md` entry added.
- [ ] `DECISIONS.md` updated if the change shifts an architectural choice.

## What "done" means for a strategy

See [`docs/EVALUATION.md`](docs/EVALUATION.md). A strategy reaches `live`
status only via the promotion path described in [`AGENTS.md`](AGENTS.md).

## Forbidden in PRs

- "should work" / "left as an exercise" — replace with verification or mark
  the change `partial`.
- Skipped tests without a linked issue.
- Drive-by refactors mixed into a feature PR — split them.
