"""Inv-1 e2e: every order passes through RiskEngine.check_and_size → Broker.place_order.

The test demonstrates the real pipeline path that the runner wires:
  Strategy.target_positions → RiskEngine.check_and_size → PaperBroker.place_order

Two scenarios are exercised:
1. Kill-switch engaged: risk rejects, ha_risk_decisions gets a reject row, no Fill is produced.
2. Valid trade: risk accepts, PaperBroker fills, ha_risk_decisions gets an accept row.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from data.db import connect
from data.repositories.audit.duckdb_risk_audit import DuckDBRiskAudit
from execution.brokers.paper import PaperBroker
from monitoring.audit.verifier import verify_table
from risk.engine import RiskEngine
from risk.errors import RiskCheckRejected
from risk.limits import RiskLimits
from risk.types import Portfolio, TargetPosition
from runs.isolation import bind_run_context, clear_run_context
from strategies.base import MarketState
from strategies.examples.momentum_xover import MomentumXover


def _portfolio(cash: float = 100_000.0) -> Portfolio:
    return Portfolio(ts=datetime.now(tz=UTC), cash=cash, high_water_mark=cash)


def _bars_uptrend(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    price = 100.0 * (1 + rng.normal(0.001, 0.005, n)).cumprod()
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": price,
            "high": price * 1.001,
            "low": price * 0.999,
            "close": price,
            "volume": 1_000.0,
            "quote_volume": 1_000.0 * price,
        },
        index=idx,
    )


@pytest.mark.e2e
def test_kill_switch_rejects_and_no_fill(tmp_path: Path) -> None:
    """Kill switch engaged → RiskEngine raises, ha_risk_decisions has reject row, no Fill."""
    db = tmp_path / "ks.duckdb"
    conn = connect(db)
    audit = DuckDBRiskAudit(conn)
    engine = RiskEngine(RiskLimits(kill_switch=True), audit=audit, run_id="run-ks")
    broker = PaperBroker(starting_cash=100_000.0)
    broker.update_mark("BTCUSDT", 50_000.0)

    bind_run_context(run_id="run-ks")
    try:
        targets = [TargetPosition(symbol="BTCUSDT", weight=0.5)]
        portfolio = _portfolio()
        with pytest.raises(RiskCheckRejected):
            engine.check_and_size(
                targets,
                portfolio,
                marks={"BTCUSDT": 50_000.0},
                realized_vol={"BTCUSDT": 0.02},
            )

        rows = conn.execute(
            """
            SELECT
                json_extract_string(payload_json, '$.outcome') AS outcome,
                json_extract_string(payload_json, '$.rule')    AS rule
            FROM ha_risk_decisions
            WHERE run_id = 'run-ks'
            """
        ).fetchall()
        assert len(rows) == 1, "expected exactly one reject row"
        assert rows[0][0] == "reject"
        assert rows[0][1] == "kill_switch"

        ok, msg = verify_table(conn, "ha_risk_decisions")
        assert ok, msg

        assert broker.cash == 100_000.0, "no fill should have occurred"
        assert broker._positions == {}
    finally:
        clear_run_context()
        conn.close()


@pytest.mark.e2e
def test_valid_target_fills_through_risk(tmp_path: Path) -> None:
    """Valid target → risk accepts → PaperBroker fills → ha_risk_decisions accept row."""
    db = tmp_path / "ok.duckdb"
    conn = connect(db)
    audit = DuckDBRiskAudit(conn)
    engine = RiskEngine(RiskLimits.model_validate({}), audit=audit, run_id="run-ok")
    broker = PaperBroker(starting_cash=100_000.0)
    broker.update_mark("BTCUSDT", 50_000.0)

    bind_run_context(run_id="run-ok")
    try:
        targets = [TargetPosition(symbol="BTCUSDT", weight=0.1)]
        portfolio = _portfolio(100_000.0)
        orders = engine.check_and_size(
            targets, portfolio, marks={"BTCUSDT": 50_000.0}, realized_vol={"BTCUSDT": 0.02}
        )
        assert orders, "expected at least one order"
        fills = asyncio.run(_place_all(broker, orders))
        assert fills, "expected fills from PaperBroker"

        rows = conn.execute(
            """
            SELECT json_extract_string(payload_json, '$.outcome') AS outcome
            FROM ha_risk_decisions
            WHERE run_id = 'run-ok'
            """
        ).fetchall()
        outcomes = [r[0] for r in rows]
        assert "accept" in outcomes, f"expected accept row, got {outcomes}"

        ok, msg = verify_table(conn, "ha_risk_decisions")
        assert ok, msg
    finally:
        clear_run_context()
        conn.close()


@pytest.mark.e2e
def test_strategy_to_broker_pipeline(tmp_path: Path) -> None:
    """Full pipeline: MomentumXover.target_positions → risk → PaperBroker.place_order."""
    db = tmp_path / "full.duckdb"
    conn = connect(db)
    audit = DuckDBRiskAudit(conn)
    engine = RiskEngine(RiskLimits.model_validate({}), audit=audit, run_id="run-full")
    broker = PaperBroker(starting_cash=100_000.0)
    bars = _bars_uptrend(n=200)
    broker.update_mark("BTCUSDT", float(bars["close"].iloc[-1]))

    strategy = MomentumXover(
        universe=["BTCUSDT"], timeframe="1h", fast=5, slow=20, target_weight=0.5
    )
    state = MarketState(ts=bars.index[-1], bars={"BTCUSDT": bars})
    targets = strategy.target_positions(state)

    bind_run_context(run_id="run-full")
    try:
        portfolio = _portfolio(100_000.0)
        mark = float(bars["close"].iloc[-1])
        try:
            orders = engine.check_and_size(
                targets, portfolio, marks={"BTCUSDT": mark}, realized_vol={"BTCUSDT": 0.02}
            )
        except RiskCheckRejected:
            orders = []

        asyncio.run(_place_all(broker, orders))

        rows = conn.execute(
            """
            SELECT json_extract_string(payload_json, '$.outcome') AS outcome
            FROM ha_risk_decisions
            WHERE run_id = 'run-full'
            """
        ).fetchall()
        assert rows, "expected at least one audit row from check_and_size"

        ok, msg = verify_table(conn, "ha_risk_decisions")
        assert ok, msg
    finally:
        clear_run_context()
        conn.close()


async def _place_all(broker: PaperBroker, orders: list) -> list:  # type: ignore[type-arg]
    fills = []
    for o in orders:
        eid = await broker.place_order(o)
        fills.append(eid)
    return fills
