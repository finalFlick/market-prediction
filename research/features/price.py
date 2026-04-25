"""Price-derived features: returns, realized volatility, z-scores."""

from __future__ import annotations

import numpy as np
import pandas as pd

from research.features.base import require_columns


def log_returns(df: pd.DataFrame) -> pd.Series:
    """Bar-to-bar log return on close. Shift-safe."""
    require_columns(df, ["close"])
    return np.log(df["close"].astype(float)).diff().rename("ret_log_1")


def realized_vol(df: pd.DataFrame, window: int = 24) -> pd.Series:
    """Rolling stdev of log returns over `window` bars (annualization is left to caller)."""
    if window < 2:
        raise ValueError("window must be >= 2")
    r = log_returns(df)
    return r.rolling(window).std().rename(f"vol_{window}")


def zscore_close(df: pd.DataFrame, window: int = 96) -> pd.Series:
    """Rolling z-score of close vs its own mean/std. Shift-safe."""
    require_columns(df, ["close"])
    if window < 5:
        raise ValueError("window must be >= 5")
    c = df["close"].astype(float)
    mu = c.rolling(window).mean()
    sd = c.rolling(window).std()
    return ((c - mu) / sd).rename(f"close_z_{window}")
