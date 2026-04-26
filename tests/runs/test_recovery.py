"""Day-0 Invariant 6: fail-closed restart transitions open runs to failed."""

from __future__ import annotations

from pathlib import Path

from data.db import connect
from runs.orchestrator import RunOrchestrator
from runs.recovery import transition_open_runs_to_failed
from runs.types import RunConfig


def _submit(db: Path, run_id: str, run_type: str = "paper", mode: str = "paper") -> None:
    o = RunOrchestrator(db_path=db)
    o.submit(RunConfig(run_id=run_id, run_type=run_type, mode=mode))  # type: ignore[call-arg]


def test_queued_run_transitioned_to_failed(tmp_path: Path) -> None:
    db = tmp_path / "r.duckdb"
    _submit(db, "run-q")
    n = transition_open_runs_to_failed(db, reason="container_restart")
    assert n == 1
    conn = connect(db)
    row = conn.execute(
        "SELECT status, error_reason FROM runs WHERE run_id = 'run-q'"
    ).fetchone()
    conn.close()
    assert row is not None
    assert row[0] == "failed"
    assert row[1] == "container_restart"


def test_running_and_paused_also_transitioned(tmp_path: Path) -> None:
    db = tmp_path / "r2.duckdb"
    _submit(db, "run-a")
    _submit(db, "run-b")
    conn = connect(db)
    conn.execute("UPDATE runs SET status = 'running' WHERE run_id = 'run-a'")
    conn.execute("UPDATE runs SET status = 'paused' WHERE run_id = 'run-b'")
    conn.close()
    n = transition_open_runs_to_failed(db, reason="container_restart")
    assert n == 2
    conn = connect(db)
    rows = conn.execute(
        "SELECT status FROM runs WHERE run_id IN ('run-a', 'run-b')"
    ).fetchall()
    conn.close()
    assert all(r[0] == "failed" for r in rows)


def test_succeeded_run_is_not_transitioned(tmp_path: Path) -> None:
    db = tmp_path / "r3.duckdb"
    _submit(db, "run-s")
    conn = connect(db)
    conn.execute("UPDATE runs SET status = 'succeeded' WHERE run_id = 'run-s'")
    conn.close()
    n = transition_open_runs_to_failed(db)
    assert n == 0


def test_state_transitions_row_written(tmp_path: Path) -> None:
    db = tmp_path / "r4.duckdb"
    _submit(db, "run-t")
    transition_open_runs_to_failed(db, reason="container_restart")
    conn = connect(db)
    row = conn.execute(
        "SELECT to_status, reason, actor FROM state_transitions WHERE run_id = 'run-t'"
    ).fetchone()
    conn.close()
    assert row is not None
    assert row[0] == "failed"
    assert row[1] == "container_restart"
    assert row[2] == "system"


def test_orchestrator_on_boot_transitions_open_runs(tmp_path: Path) -> None:
    db = tmp_path / "r5.duckdb"
    _submit(db, "run-boot")
    o = RunOrchestrator(db_path=db)
    n, reports = o.on_boot()
    assert n == 1
    assert reports == []
