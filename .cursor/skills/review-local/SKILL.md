---
name: review-local
description: Quick local audit of changed files for AI slop, secrets, and trading-lab style violations before committing or opening a PR. Use this skill before any `git commit` or PR-creation request.
---

# review-local

Project-tuned variant of the user-level `review-local` skill. This one
adds trading-lab-specific checks: no risk-bypass flags, no LLM imports
in `execution/`, no hardcoded position sizes.

## When to use

- The user asks to commit, push, or open a PR.
- The user asks to "audit", "review my changes", "check before commit".
- Triggered automatically by the `pre_commit_review` hook on `git commit`.

## Procedure

Run each check sequentially. Each must pass; otherwise the skill exits
with a clear `FAIL: <reason>`.

1. **Diff scope.** `git status --short` and `git diff --name-only`. If
   the diff touches both `risk/` and `execution/`, **stop** and ask the
   user to split the PR (cross-cutting changes need separate review).

2. **Secrets scan.** Run gitleaks if available:
   ```bash
   gitleaks protect --staged --no-banner
   ```
   Otherwise grep for the patterns in
   `tests/security/test_no_secrets.py`. Any hit → FAIL.

3. **Risk-bypass scan.** Forbidden tokens:
   ```
   skip_risk | bypass_risk | RISK_BYPASS | DISABLE_RISK | --no-risk
   ```
   Any hit → FAIL.

4. **LLM-isolation scan.** No new file under `execution/` may import
   `research.llm`. Run:
   ```bash
   pytest tests/security/test_llm_isolation.py -q
   ```
   Red → FAIL.

5. **AI slop check.** Grep the diff for forbidden phrases:
   `should work`, `left as an exercise`, `verified offline`,
   `// TODO without owner`. Any hit → FAIL.

6. **Tests + lint.**
   ```bash
   pytest -q
   ruff check .
   mypy --strict --explicit-package-bases data research strategies risk backtests execution monitoring backend
   ```
   Any red → FAIL.

7. **Backtest smoke (if pipeline files touched).**
   ```bash
   python -m backtests.smoke
   ```

## Outputs

- A 7-line checklist with `OK` / `FAIL: <reason>` per check.
- If FAIL on any line: do not commit. Surface the exact command and
  output to the user.
- If PASS: a one-line green summary and proceed with commit.

## Forbidden

- Skipping checks because they're "noisy" — they exist for a reason.
- Auto-fixing risk/security findings. They require human review.
- Committing without running this skill when the diff touches `risk/`,
  `execution/`, or `configs/risk.yaml` ([`risk-management.mdc`](mdc:.cursor/rules/risk-management.mdc)).
