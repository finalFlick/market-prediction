"""RiskEngine emits `RiskDecision` records when an audit sink is attached."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from risk.audit import InMemoryRiskAudit
from risk.engine import RiskEngine
from risk.errors import RiskCheckRejected
from risk.limits import RiskLimits
from risk.types import Portfolio, TargetPosition


def _p() -> Portfolio:
    return Portfolio(ts=datetime.now(tz=UTC), cash=100_000.0, high_water_mark=100_000.0)


def test_reject_path_emits_reject() -> None:
    audit = InMemoryRiskAudit()
    engine = RiskEngine(RiskLimits(kill_switch=True), audit=audit, run_id="r1")
    with pytest.raises(RiskCheckRejected):
        engine.check_and_size([], _p(), marks={}, realized_vol={})
    assert any(d.outcome == "reject" and d.rule == "kill_switch" for d in audit.items)


def test_accept_path_emits_accept() -> None:
    audit = InMemoryRiskAudit()
    engine = RiskEngine(
        RiskLimits.model_validate({}),
        audit=audit,
    )
    engine.check_and_size(
        [TargetPosition(symbol="BTCUSDT", weight=0.1)],
        _p(),
        marks={"BTCUSDT": 50_000.0},
        realized_vol={"BTCUSDT": 0.02},
    )
    assert any(
        d.outcome == "accept" and d.rule == "check_and_size" and d.details.get("n_orders", 0) >= 0
        for d in audit.items
    )


def test_skip_missing_data_emits_skip() -> None:
    audit = InMemoryRiskAudit()
    engine = RiskEngine(RiskLimits.model_validate({}), audit=audit)
    engine.check_and_size(
        [TargetPosition(symbol="BTCUSDT", weight=0.1)],
        _p(),
        marks={},
        realized_vol={},
    )
    assert any(d.outcome == "skip" and d.rule == "missing_market_data" for d in audit.items)
