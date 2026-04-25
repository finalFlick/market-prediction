"""Byte-identical metrics for identical backtest inputs (Day-0 Invariant 3)."""

from __future__ import annotations

import pytest

from backtests.engine import BacktestConfig, BacktestEngine, CostModel
from backtests.metrics import compute_metrics
from backtests.smoke import _synthetic_bars
from monitoring.canonical_json import canonical_dumps
from risk.limits import RiskLimits
from strategies.examples.momentum_xover import MomentumXover


@pytest.mark.det
def test_identical_runs_produce_identical_canonical_metrics() -> None:
    bars = {"BTCUSDT": _synthetic_bars(n=400, seed=7)}
    strategy = MomentumXover(
        name="det_momo",
        universe=["BTCUSDT"],
        timeframe="1h",
        fast=5,
        slow=20,
        target_weight=0.4,
    )
    cfg = BacktestConfig(
        starting_cash=10_000.0,
        cost_model=CostModel(taker_fee_bps=5.0, slippage_bps=2.0, latency_bars=0),
        risk_limits=RiskLimits.model_validate({}),
        seed=42,
    )
    a = BacktestEngine(cfg).run(strategy, bars)
    b = BacktestEngine(cfg).run(strategy, bars)
    assert canonical_dumps(compute_metrics(a.equity, a.trades)) == canonical_dumps(
        compute_metrics(b.equity, b.trades)
    )
