## What changed

<!-- 1-5 bullets -->

## Verification

- [ ] `pytest -q -m "not slow and not integration and not e2e"`
- [ ] `pytest -q -m e2e` (if API/flows touched)
- [ ] `ruff check .` and `ruff format --check .`
- [ ] `mypy --strict --explicit-package-bases .`
- [ ] `python -m backtests.smoke` (if backtest path touched)
- [ ] `python -m monitoring.audit verify --tables critical` (if audit path touched)

## Risks / edge cases

<!-- -->
