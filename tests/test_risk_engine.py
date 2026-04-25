"""Risk engine: happy path and rejection paths."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from risk.engine import RiskEngine
from risk.errors import RiskCheckRejected
from risk.limits import RiskLimits
from risk.types import Portfolio, TargetPosition


def _portfolio(cash: float = 100_000.0) -> Portfolio:
    return Portfolio(ts=datetime.now(tz=UTC), cash=cash, high_water_mark=cash)


def test_kill_switch_rejects() -> None:
    engine = RiskEngine(RiskLimits(kill_switch=True))
    with pytest.raises(RiskCheckRejected, match="kill_switch"):
        engine.check_and_size([], _portfolio(), marks={}, realized_vol={})


def test_per_symbol_weight_cap() -> None:
    engine = RiskEngine(RiskLimits(max_per_symbol_weight=0.3))
    targets = [TargetPosition(symbol="BTCUSDT", weight=0.5)]
    with pytest.raises(RiskCheckRejected, match="max_per_symbol_weight"):
        engine.check_and_size(
            targets, _portfolio(), marks={"BTCUSDT": 50_000.0}, realized_vol={"BTCUSDT": 0.01}
        )


def test_happy_path_emits_buy_order() -> None:
    engine = RiskEngine(RiskLimits(target_annual_vol=0.10))
    targets = [TargetPosition(symbol="BTCUSDT", weight=0.5)]
    orders = engine.check_and_size(
        targets,
        _portfolio(),
        marks={"BTCUSDT": 50_000.0},
        realized_vol={"BTCUSDT": 0.01},
    )
    assert len(orders) == 1
    assert orders[0].symbol == "BTCUSDT"
    assert orders[0].side.value == "buy"
    assert orders[0].quantity > 0


def test_missing_market_data_skips_symbol() -> None:
    engine = RiskEngine(RiskLimits())
    targets = [TargetPosition(symbol="BTCUSDT", weight=0.1)]
    orders = engine.check_and_size(targets, _portfolio(), marks={}, realized_vol={})
    assert orders == []
