# Contributing to trading-lab

This repository is **public** on GitHub. Everyone — including agents and fork
contributors — should assume **untrusted code** may run in CI for pull
requests opened from forks.

## Before you open a PR

- Follow [`WORKFLOW.md`](../WORKFLOW.md) and [`.cursor/rules/workflow.mdc`](../.cursor/rules/workflow.mdc).
- Do not paste secrets, API keys, or exchange credentials in issues or PRs.
- Risk- and execution-critical changes need human review per
  [`.cursor/rules/risk-management.mdc`](../.cursor/rules/risk-management.mdc).

## Fork PR and CI security (read once)

- Workflows triggered by **`pull_request` from a fork** receive a read-only
  `GITHUB_TOKEN` and **cannot** access repository secrets (unless a maintainer
  has misconfigured the workflow). That is intentional.
- Avoid patterns that combine **`pull_request_target`** with a checkout of the
  PR head ref and privileged steps — that pattern is a common way to steal
  secrets on public repos.
- Prefer **`pull_request`** for building and testing contributor code. Reserve
  elevated permissions for jobs that run only on `push` to protected branches,
  **`workflow_run`** after merge, or **GitHub Environments** with required
  reviewers.

## Maintainer checklist (GitHub settings)

Configure these in **Repository → Settings** (and organization settings if
applicable). Re-verify after transferring the repo or changing visibility.

| Item | Purpose |
|------|---------|
| **Rulesets** on `main` | Require status checks from CI; block force-push; optional linear history. |
| **Actions → General → Workflow permissions** | Default `GITHUB_TOKEN` to **read-only**; grant write only in jobs that need it. |
| **Code security and analysis** | Enable **Dependabot alerts** and **Dependabot security updates**; enable **Code scanning** (CodeQL). |
| **Secret scanning** + **Push protection** | Block accidental secret commits (complements `gitleaks` in CI). |
| **CODEOWNERS** | Requires real `@user` or `@org/team` handles in [`.github/CODEOWNERS`](../.github/CODEOWNERS); update if maintainers change. |
| **Fork PR workflow audit** | Confirm no job running fork code uses `secrets.*` except where GitHub explicitly allows safe patterns. |

Spec traceability: platform work maps to **FEATURE-0039** (CI gates),
**FEATURE-0040** (secrets and controls), and **FEATURE-0003** (contribution
governance) under `specs/trading-lab-platform/`.

## Local verification

Match CI as closely as possible before pushing:

```bash
pytest -q -m "not slow and not integration and not e2e"
ruff check . && ruff format --check .
mypy --strict --explicit-package-bases .
pytest -q -m e2e
python -m backtests.smoke
```

See [`RUNNING.md`](../RUNNING.md) for Docker-first development.
