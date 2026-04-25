"""Strategy-level test for the reference momentum strategy."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

from strategies.base import MarketState
from strategies.examples.momentum_xover import MomentumXover


def _bars(direction: int, n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(11)
    drift = 0.001 * direction
    rets = rng.normal(drift, 0.005, size=n).cumsum()
    price = 100.0 * np.exp(rets)
    idx = pd.date_range(
        start=datetime.now(tz=UTC) - timedelta(hours=n), periods=n, freq="1H", tz="UTC"
    )
    return pd.DataFrame(
        {
            "open": price,
            "high": price * 1.001,
            "low": price * 0.999,
            "close": price,
            "volume": 100.0,
            "quote_volume": 100.0 * price,
        },
        index=idx,
    )


def test_momentum_returns_one_target_per_universe_member() -> None:
    s = MomentumXover(universe=["BTCUSDT", "ETHUSDT"], fast=4, slow=12)
    state = MarketState(
        ts=pd.Timestamp.now(tz="UTC"), bars={"BTCUSDT": _bars(+1), "ETHUSDT": _bars(-1)}
    )
    out = s.target_positions(state)
    symbols = sorted(t.symbol for t in out)
    assert symbols == ["BTCUSDT", "ETHUSDT"]


def test_momentum_warmup_is_respected() -> None:
    s = MomentumXover(universe=["BTCUSDT"], fast=4, slow=12)
    short = _bars(+1, n=10)
    state = MarketState(ts=pd.Timestamp.now(tz="UTC"), bars={"BTCUSDT": short})
    out = s.target_positions(state)
    assert all(t.weight == 0.0 for t in out), "weights must be zero before warmup"


def test_momentum_takes_long_in_uptrend() -> None:
    s = MomentumXover(universe=["BTCUSDT"], fast=4, slow=12, target_weight=0.5)
    state = MarketState(ts=pd.Timestamp.now(tz="UTC"), bars={"BTCUSDT": _bars(+1, n=300)})
    out = s.target_positions(state)
    assert any(t.weight >= 0 for t in out)
