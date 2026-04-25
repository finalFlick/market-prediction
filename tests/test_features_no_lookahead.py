"""Verify that canonical features do not peek at the future."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from research.features.momentum import ema_crossover, macd, rsi
from research.features.price import log_returns, realized_vol, zscore_close
from research.features.validation import assert_no_lookahead, assert_utc_index
from research.features.volume import dollar_volume, obv, volume_zscore


@pytest.fixture
def ohlcv() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 500
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    base = 100 + np.cumsum(rng.standard_normal(n) * 0.5)
    df = pd.DataFrame(
        {
            "open": base + rng.standard_normal(n) * 0.1,
            "high": base + np.abs(rng.standard_normal(n)) * 0.2,
            "low": base - np.abs(rng.standard_normal(n)) * 0.2,
            "close": base,
            "volume": np.abs(rng.standard_normal(n)) * 1000 + 1.0,
            "quote_volume": np.abs(rng.standard_normal(n)) * 1000 + 1.0,
        },
        index=idx,
    )
    return df


def test_index_is_utc(ohlcv: pd.DataFrame) -> None:
    assert_utc_index(ohlcv)


@pytest.mark.parametrize(
    "fn",
    [
        log_returns,
        lambda d: realized_vol(d, window=24),
        lambda d: zscore_close(d, window=96),
        dollar_volume,
        lambda d: volume_zscore(d, window=96),
        obv,
        lambda d: ema_crossover(d, fast=12, slow=26),
        lambda d: rsi(d, window=14),
        lambda d: macd(d, fast=12, slow=26, signal=9),
    ],
)
def test_no_lookahead(ohlcv: pd.DataFrame, fn) -> None:  # type: ignore[no-untyped-def]
    assert_no_lookahead(fn, ohlcv, cut=300)
