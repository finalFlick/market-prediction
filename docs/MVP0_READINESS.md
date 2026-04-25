# MVP-0 readiness

This checklist maps **Day-0 Invariants 1–8** and MVP-0 acceptance to **evidence commands**.

| Invariant | Evidence |
|----------|----------|
| 1 Risk non-bypassable | `pytest tests/security/test_risk_engine_non_bypassable.py tests/security/test_risk_path_only.py tests/risk/` |
| 2 LLM isolation | `pytest tests/security/test_llm_isolation.py tests/security/test_runs_llm_isolation.py` |
| 3 Determinism | `pytest -q -m det` |
| 4 Hash-chain audit | `python -m monitoring.audit verify --tables critical` |
| 5 Run isolation | `runs/isolation.py` + future repo guards |
| 6 Fail-closed restart | `runs/recovery.py` + `RunOrchestrator.on_boot` |
| 7 Redis transport + outbox | `runs/events/outbox.py` + `tests/integration/test_outbox_idempotency.py` |
| 8 Live adapter lock | `tests/security/test_live_registration_forbidden.py` |

**Quality bar:** `ruff check .`, `mypy --strict --explicit-package-bases .`, `pytest -q -m "not slow and not integration and not e2e"`, `pytest -q -m e2e`, `python -m backtests.smoke`, `node frontend` build in CI.

See also [SECURITY.md](SECURITY.md) and [DECISIONS.md](../DECISIONS.md) (DEC-007/008/009).

**Deferred past MVP-0 (tracked for v1):** `GET /api/sse/runs/{id}` (live event stream to dashboard), full Redis Streams bus beyond the DuckDB outbox + idempotency test.
