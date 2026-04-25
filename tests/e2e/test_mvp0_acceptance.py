"""MVP-0 acceptance gate (subset of design § MVP-0 Acceptance)."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.app import create_app
from data.db import connect
from data.repositories.audit.chain import append_row
from execution.brokers.binance import BinanceLive
from execution.brokers.registry import LiveAdapterRegistrationForbidden, LiveBrokerRegistry
from learning.scorers.standard import apply_scorers, make_default_scorers
from learning.types import RunSummary
from monitoring.audit.verifier import verify_all
from runs.orchestrator import RunOrchestrator
from runs.types import RunConfig


@pytest.mark.e2e
def test_mvp0_acceptance_subset(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "mvp.duckdb"
    monkeypatch.setenv("DUCKDB_PATH", str(db))
    c = connect(db)
    append_row(
        c,
        "ha_risk_decisions",
        natural_key="nd1",
        payload={"x": 1},
        run_id="r0",
    )
    c.close()
    r = verify_all(db_path=db, tables="critical")
    assert r["all_ok"] is True

    reg = LiveBrokerRegistry(unlocked_provider=lambda: False)
    with pytest.raises(LiveAdapterRegistrationForbidden):
        reg.register(BinanceLive())

    ro = RunOrchestrator(db_path=db)
    rid = ro.submit(RunConfig(run_id="accept-1", run_type="backtest", mode="dry_run"))
    assert rid == "accept-1"

    sc = make_default_scorers(str(db))
    apply_scorers(
        sc,
        RunSummary(
            run_id="accept-1",
            oos_metrics={"sharpe": 0.5, "max_drawdown": -0.1, "hit_rate": 0.45},
        ),
    )

    client = TestClient(create_app())
    h = client.get("/api/system/health")
    assert h.status_code == 200
    assert h.json().get("audit_chain_ok") is True
    runs = client.get("/api/runs")
    assert runs.status_code == 200
    assert "items" in runs.json()
