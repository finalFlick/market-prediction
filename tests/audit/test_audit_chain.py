"""Hash-chained ha_* tables (Day-0 Invariant 4)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from data.db import connect
from data.repositories.audit.chain import append_row
from data.repositories.audit.duckdb_risk_audit import DuckDBRiskAudit
from monitoring.audit.verifier import verify_all, verify_table
from risk.engine import RiskEngine
from risk.errors import RiskCheckRejected
from risk.limits import RiskLimits
from risk.types import Portfolio, TargetPosition


def test_append_two_rows_verifies(
    tmp_path: Path,
) -> None:
    p = tmp_path / "a.duckdb"
    con = connect(p)
    append_row(
        con,
        "ha_risk_decisions",
        natural_key="d1",
        payload={"a": 1},
        run_id="r1",
    )
    append_row(
        con,
        "ha_risk_decisions",
        natural_key="d2",
        payload={"a": 2},
        run_id="r1",
    )
    ok, msg = verify_table(con, "ha_risk_decisions")
    assert ok, msg
    con.close()


def test_duckdb_risk_audit_and_riskengine_path(
    tmp_path: Path,
) -> None:
    p = tmp_path / "a.duckdb"
    con = connect(p)
    sink = DuckDBRiskAudit(con)
    engine = RiskEngine(RiskLimits(kill_switch=True), audit=sink, run_id="r1")
    port = Portfolio(ts=datetime.now(tz=UTC), cash=1.0)
    with pytest.raises(RiskCheckRejected):
        engine.check_and_size(
            [TargetPosition(symbol="BTC", weight=0.1)],
            port,
            marks={"BTC": 1.0},
            realized_vol={"BTC": 0.01},
        )
    ok, m = verify_table(con, "ha_risk_decisions")
    assert ok, m
    con.close()


def test_cli_verify_on_empty(tmp_path: Path) -> None:
    p = tmp_path / "a.duckdb"
    c = connect(p)
    c.close()
    r = verify_all(db_path=p, tables="critical")
    assert r["all_ok"] is True
