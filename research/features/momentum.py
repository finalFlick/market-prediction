"""Momentum / oscillator features: EMA crossovers, RSI, MACD."""

from __future__ import annotations

import numpy as np
import pandas as pd

from research.features.base import require_columns


def ema(series: pd.Series, span: int) -> pd.Series:
    if span < 2:
        raise ValueError("span must be >= 2")
    return series.ewm(span=span, adjust=False).mean()


def ema_crossover(df: pd.DataFrame, fast: int = 12, slow: int = 26) -> pd.Series:
    """Normalized EMA crossover: (EMA_fast - EMA_slow) / EMA_slow."""
    require_columns(df, ["close"])
    if fast >= slow:
        raise ValueError("fast must be < slow")
    c = df["close"].astype(float)
    return ((ema(c, fast) - ema(c, slow)) / ema(c, slow)).rename(f"ema_xover_{fast}_{slow}")


def rsi(df: pd.DataFrame, window: int = 14) -> pd.Series:
    """Wilder's RSI."""
    require_columns(df, ["close"])
    if window < 2:
        raise ValueError("window must be >= 2")
    delta = df["close"].astype(float).diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / window, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / window, adjust=False).mean()
    rs = gain / loss.replace(0.0, np.nan)
    return (100 - 100 / (1 + rs)).rename(f"rsi_{window}")


def macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Classic MACD line, signal line, and histogram."""
    require_columns(df, ["close"])
    c = df["close"].astype(float)
    macd_line = ema(c, fast) - ema(c, slow)
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return pd.DataFrame(
        {
            f"macd_{fast}_{slow}": macd_line,
            f"macd_signal_{signal}": signal_line,
            f"macd_hist_{fast}_{slow}_{signal}": hist,
        }
    )
