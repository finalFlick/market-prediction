"""Acc-B e2e: BacktestRun shows up in GET /api/runs and GET /api/backtests after execution."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.app import create_app
from runs.orchestrator import RunOrchestrator
from runs.types import RunConfig
from runs.worker import RunWorker


@pytest.mark.e2e
def test_backtest_run_appears_in_api(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db = tmp_path / "bt.duckdb"
    results_root = tmp_path / "results"
    results_root.mkdir()

    monkeypatch.setenv("DUCKDB_PATH", str(db))

    cfg = RunConfig(
        run_id="bt-api-test-1",
        run_type="backtest",
        mode="backtest",
        strategy_dotted="strategies.examples.momentum_xover.MomentumXover",
        capital=10_000.0,
        seed=7,
    )
    o = RunOrchestrator(db_path=db)
    o.submit(cfg)

    worker = RunWorker(db_path=db, results_root=results_root)
    ok = worker.process_one(cfg)
    assert ok, "expected backtest run to succeed"

    client = TestClient(create_app())

    runs_resp = client.get("/api/runs")
    assert runs_resp.status_code == 200
    runs_items = runs_resp.json()["items"]
    run_ids = [r["run_id"] for r in runs_items]
    assert "bt-api-test-1" in run_ids, f"run not found in /api/runs: {run_ids}"

    run_detail = client.get("/api/runs/bt-api-test-1")
    assert run_detail.status_code == 200
    assert run_detail.json()["status"] == "succeeded"

    bt_resp = client.get("/api/backtests")
    assert bt_resp.status_code == 200
    bt_ids = [b["run_id"] for b in bt_resp.json()]
    assert "bt-api-test-1" in bt_ids, f"backtest not found in /api/backtests: {bt_ids}"

    bt_detail = client.get("/api/backtests/bt-api-test-1")
    assert bt_detail.status_code == 200
    assert bt_detail.json()["sharpe"] is not None


@pytest.mark.e2e
def test_backtest_run_byte_identical_rerun(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Re-running the same BacktestSpec produces identical Sharpe (Inv-3 check via API)."""
    import hashlib  # noqa: PLC0415

    db1 = tmp_path / "bt1.duckdb"
    db2 = tmp_path / "bt2.duckdb"
    r1 = tmp_path / "r1"
    r2 = tmp_path / "r2"
    r1.mkdir()
    r2.mkdir()

    cfg = RunConfig(
        run_id="bt-det-1",
        run_type="backtest",
        mode="backtest",
        strategy_dotted="strategies.examples.momentum_xover.MomentumXover",
        capital=10_000.0,
        seed=7,
    )

    worker1 = RunWorker(db_path=db1, results_root=r1)
    RunOrchestrator(db_path=db1).submit(cfg)
    worker1.process_one(cfg)

    cfg2 = RunConfig(
        run_id="bt-det-2",
        run_type="backtest",
        mode="backtest",
        strategy_dotted="strategies.examples.momentum_xover.MomentumXover",
        capital=10_000.0,
        seed=7,
    )
    worker2 = RunWorker(db_path=db2, results_root=r2)
    RunOrchestrator(db_path=db2).submit(cfg2)
    worker2.process_one(cfg2)

    metrics1 = list(r1.glob("*/metrics.json"))
    metrics2 = list(r2.glob("*/metrics.json"))
    assert metrics1 and metrics2
    h1 = hashlib.sha256(metrics1[0].read_bytes()).hexdigest()
    h2 = hashlib.sha256(metrics2[0].read_bytes()).hexdigest()
    assert h1 == h2, "metrics.json not byte-identical across two runs with same config+seed"
