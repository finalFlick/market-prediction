# POC results (trading-lab)

Rough, throwaway scripts under `pocs/` to de-risk requirements and design. Re-run anytime from the repo root:

```text
python pocs/run_all_pocs.py
```

Individual entry points: `python pocs/<name>/run_poc.py`

**Environment:** Python 3.11+ is the project target. On the host where these were run, the system `python` was 3.9; the scripts were adjusted to run on 3.9+ without extra setup where possible. **Real `RiskEngine` import** (`pocs/risk_engine_bypass/run_poc_real.py`) needs `pip install -e .` (or your venv with project dependencies); if `structlog` and friends are missing, that script **exits 0** with `POC2b_SKIP` so the aggregate runner stays green.

---

## Summary

| # | Topic | Path | Outcome |
|---|--------|------|--------|
| 1 | Deterministic backtest / canonical metrics bytes | `pocs/deterministic_backtest/run_poc.py` | **PASS** — two runs, same `sha256` over canonical JSON (sorted keys, decimals for floats, `str` for `schema_version`). |
| 2 | Risk path not bypassed (toy) | `pocs/risk_engine_bypass/run_poc.py` | **PASS** — `GatedBroker` rejects `caller != "risk_engine"`. |
| 2b | Real `RiskEngine` | `pocs/risk_engine_bypass/run_poc_real.py` | **SKIP** here (no venv deps); with deps, proves orders only from `check_and_size`. |
| 3 | Run artifact + replay hash | `pocs/artifact_replay/run_poc.py` | **PASS** — on-disk `metrics.json` hash matches replay recompute. |
| 4 | Event stream + durable outbox | `pocs/event_stream/run_poc.py` | **PASS** — in-memory stream + **SQLite** outbox (DuckDB used if installed); after “crash”, keys match; `con.close()` for Windows file lock. |
| 5 | Paper broker (fees, slip, mkt/limit/partial) | `pocs/paperbroker_simulation/run_poc.py` | **PASS** — toy book; market pays ask+slip; limit sell at/below bid fills; buy hits partial depth. |
| 6 | LLM cannot submit orders | `pocs/llm_isolation/run_poc.py` | **PASS** — pipeline rejects `source=llm`. |
| 7 | Config snapshot per run | `pocs/config_mutation/run_poc.py` | **PASS** — run-001 frozen at 1% risk; run-002 and global at 5%. |
| 8 | Learning / signal scoreboard | `pocs/learning_feedback/run_poc.py` | **PASS (informational)** — with one seed, **sentiment** ranked first by raw PnL sum; shows ranking can be **noise** without OOS protocol. |
| + | Momentum / mean-rev / Hurst proxy (synthetic) | `pocs/signal_validity_experiments/run_poc.py` | **PASS** — positive cross-sectional mom proxy on synthetic data with baked-in factor; not a live edge claim. |
| Bonus | Latency + 1M-row pipeline | `pocs/bonus_latency_pipeline/run_poc.py` | **PASS** — ~0.01s order of magnitude for 1M rows + returns on this machine. |

---

## Captured run (one host)

```text
OK  pocs\deterministic_backtest\run_poc.py
    POC1_OK
    sha256(metrics.json bytes) = 072abd5c785ec5076225268ce88fbfec3faf68afc1e88f64f0e5339fe1ea8890
OK  pocs\risk_engine_bypass\run_poc.py
    POC2_OK: direct strategy->broker blocked; risk_engine path allowed
OK  pocs\risk_engine_bypass\run_poc_real.py
    POC2b_SKIP: project deps not installed (need structlog, etc.): No module named 'structlog' Run: pip install -e .  then re-run this script.
OK  pocs\artifact_replay\run_poc.py
    POC3_OK: replay metrics hash matches stored metrics hash
OK  pocs\event_stream\run_poc.py
    POC4_OK: outbox==replay; transport=in_memory; store=sqlite (DuckDB in full stack; SQLite OK for POC if no duckdb installed)
OK  pocs\paperbroker_simulation\run_poc.py
    POC5_OK: market, limit+partial, fees+slip monotonic; cross-check vs reference mid inside band
OK  pocs\llm_isolation\run_poc.py
    POC6_OK: malicious LLM text is not admitted as a submit_from_strategy order
OK  pocs\config_mutation\run_poc.py
    POC7_OK: first run snapshot frozen; second run and global at 5%
OK  pocs\learning_feedback\run_poc.py
    POC8_INFO: with this seed, ranking order: ['sentiment', 'volume_spike', 'momentum'] ...
OK  pocs\signal_validity_experiments\run_poc.py
    ...
OK  pocs\bonus_latency_pipeline\run_poc.py
    ...
```

(Exact timing lines will vary by CPU.)

---

## Implications for requirements / design

1. **Determinism** — Achievable for this POC’s metrics object if serialization rules are strict (strings, sorted keys, fixed decimal format). Vectorized / third-party libs still need version pins in production.
2. **Risk** — Architectural enforcement (toy) + importable `RiskEngine` when the full environment is available. **CI** should run `run_poc_real` in the real venv.
3. **Artifact replay** — Viable: persist `config` + `data` identity; recompute and compare **hash of canonical metrics**.
4. **Events** — **Redis = transport, DB = truth** is validated in miniature: outbox rows survive; replay set equals processed keys; idempotency on natural key in SQLite/duckdb pattern.
5. **Paper** — A minimal fee/slip/depth model can behave sensibly; production must add regression tests against known fills.
6. **LLM** — Isolation is a **policy + API** problem: block `llm` as an order `source` and never wire LLM text into `submit_from_strategy` without a numeric feature layer.
7. **Config** — `deepcopy` at run start is enough for POC; product should use explicit `config_version` and immutable `run` rows.
8. **Learning** — Raw score ranking **without** held-out OOS and stability checks can **invert** the intended order vs.injected “edge” (this seed: sentiment wins). **Design should require** purged/embargo’d evaluation and minimum sample sizes before any auto-apply of lever scores.
9. **“Does the market have structure?”** — Synthetic panel shows the **momentum** toy can be positive; real data and costs are still gating. No change to the rule: **data → signal experiments before scaling infra.**

---

## Follow-ups (not blockers for POC)

- Re-run `run_poc_real.py` inside a venv with `pip install -e .` and add one CI job.
- If Redis is up, POC4 can use a real `xadd` (code path already attempts Redis then falls back).
- Add real OHLCV slice for `signal_validity` when data paths exist.
