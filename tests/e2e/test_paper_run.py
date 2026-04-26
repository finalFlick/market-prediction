"""Acc-C e2e: PaperRun fills land, risk rejects visible in ha_risk_decisions."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from data.db import connect
from data.repositories.audit.duckdb_risk_audit import DuckDBRiskAudit
from risk.engine import RiskEngine
from risk.errors import RiskCheckRejected
from risk.limits import RiskLimits
from risk.types import Portfolio, TargetPosition
from runs.isolation import bind_run_context, clear_run_context
from runs.orchestrator import RunOrchestrator
from runs.types import RunConfig
from runs.worker import RunWorker


@pytest.mark.e2e
def test_paper_run_succeeds_and_has_audit_rows(tmp_path: Path) -> None:
    db = tmp_path / "paper.duckdb"
    o = RunOrchestrator(db_path=db)
    cfg = RunConfig(
        run_id="paper-test-1",
        run_type="paper",
        mode="paper",
        strategy_dotted="strategies.examples.momentum_xover.MomentumXover",
        capital=100_000.0,
        seed=42,
    )
    o.submit(cfg)

    conn = connect(db)
    row = conn.execute("SELECT status FROM runs WHERE run_id = 'paper-test-1'").fetchone()
    conn.close()
    assert row is not None and row[0] == "queued"

    worker = RunWorker(db_path=db)
    ok = worker.process_one(cfg)
    assert ok, "expected paper run to succeed"

    conn = connect(db)
    status_row = conn.execute("SELECT status FROM runs WHERE run_id = 'paper-test-1'").fetchone()
    assert status_row is not None
    assert status_row[0] == "succeeded"

    risk_rows = conn.execute(
        """
        SELECT json_extract_string(payload_json, '$.outcome') AS outcome
        FROM ha_risk_decisions
        WHERE run_id = 'paper-test-1'
        """
    ).fetchall()
    assert risk_rows, "expected at least one ha_risk_decisions row for the paper run"

    trans_rows = conn.execute(
        "SELECT to_status, actor FROM state_transitions WHERE run_id = 'paper-test-1'"
    ).fetchall()
    assert any(r[0] == "succeeded" for r in trans_rows), (
        f"no succeeded transition found: {trans_rows}"
    )
    conn.close()


@pytest.mark.e2e
def test_paper_run_with_kill_switch_records_reject(tmp_path: Path) -> None:
    """Kill-switch risk reject is visible in ha_risk_decisions; run still transitions."""
    db = tmp_path / "ks.duckdb"
    conn = connect(db)
    audit = DuckDBRiskAudit(conn)
    engine = RiskEngine(RiskLimits(kill_switch=True), audit=audit, run_id="ks-paper-1")

    bind_run_context(run_id="ks-paper-1")
    try:
        with pytest.raises(RiskCheckRejected):
            engine.check_and_size(
                [TargetPosition(symbol="BTCUSDT", weight=0.5)],
                Portfolio(ts=datetime.now(tz=UTC), cash=50_000.0, high_water_mark=50_000.0),
                marks={"BTCUSDT": 50_000.0},
                realized_vol={"BTCUSDT": 0.02},
            )
    finally:
        clear_run_context()

    rows = conn.execute(
        """
        SELECT json_extract_string(payload_json, '$.outcome') AS outcome,
               json_extract_string(payload_json, '$.rule') AS rule
        FROM ha_risk_decisions
        WHERE run_id = 'ks-paper-1'
        """
    ).fetchall()
    conn.close()
    assert rows, "expected risk audit rows"
    assert rows[0][0] == "reject"
    assert rows[0][1] == "kill_switch"
