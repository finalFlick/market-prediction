# CODING_STANDARDS

Concise rules. Full version with rationale lives in
[`.cursor/rules/coding-standards.mdc`](../.cursor/rules/coding-standards.mdc).

## Python

- **Version:** 3.11+. Use modern syntax: `list[int]`, `str | None`, `match`.
- **Type hints required** on every public function and method. CI runs
  `mypy --strict`.
- **Pure functions** wherever possible. No global mutable state. Module-level
  state is a code smell.
- **Determinism.** Data pipelines must be deterministic given the same
  inputs and seed. Use `numpy.random.default_rng(seed)`, not `np.random.*`.
- **Money is `Decimal`** (never `float`) at any boundary that hits a broker.
- **Timestamps are UTC `pd.Timestamp` (timezone-aware).** Naive datetimes are
  rejected at ingestion.
- **Logging via `monitoring.logger.get_logger(__name__)`** (structlog).
  Never log raw API keys; the logger redacts known fields.
- **Exceptions are module-specific.** `risk.errors.RiskCheckRejected`,
  `data.errors.IngestError`, etc. Don't `raise Exception(...)`.
- **Lint:** `ruff check .` and `ruff format --check .` must be green.

## TypeScript / React (frontend)

- `tsconfig.strict: true`. CI runs `npm run typecheck`.
- App Router (Next.js 14). Prefer server components; mark client islands
  with `"use client"` only when needed (charts, tables).
- All API calls go through `frontend/lib/api.ts`. Components do not
  hand-roll `fetch`.
- Tailwind for layout; design primitives live in `frontend/components/ui/`.
- File naming: `kebab-case.tsx` for files, `PascalCase` for components.

## File organization

- One package per pipeline stage (`data/`, `research/`, `strategies/`,
  `risk/`, `backtests/`, `execution/`, `monitoring/`).
- A module belongs to **one** stage. Cross-stage helpers go in the upstream
  stage and are imported, never duplicated.
- Configs are YAML in `configs/`, loaded via Pydantic models. Never hardcode
  parameters in strategy or risk code.

## Tests

- Unit: `tests/test_*.py` (top-level).
- Strategy: `tests/strategy/`.
- E2E: `tests/e2e/` (`@pytest.mark.e2e`).
- Security / invariants: `tests/security/` (`@pytest.mark.security`).
- AI prompt evals: `ai_evals/deepeval/` and `ai_evals/promptfoo/`.

## What never lands in a PR

- Commented-out code.
- TODOs without an owner and a linked issue.
- "Just-this-once" exceptions to risk, look-ahead, or LLM-isolation rules.
- Secrets, .env files, or anything matching the patterns in
  `tests/security/test_no_secrets.py`.
