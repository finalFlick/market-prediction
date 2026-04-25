"""Volume-derived features."""

from __future__ import annotations

import numpy as np
import pandas as pd

from research.features.base import require_columns


def dollar_volume(df: pd.DataFrame) -> pd.Series:
    """Approximate dollar volume = close * volume. Shift-safe."""
    require_columns(df, ["close", "volume"])
    return (df["close"].astype(float) * df["volume"].astype(float)).rename("dollar_volume")


def volume_zscore(df: pd.DataFrame, window: int = 96) -> pd.Series:
    """Rolling z-score of base-currency volume."""
    require_columns(df, ["volume"])
    if window < 5:
        raise ValueError("window must be >= 5")
    v = df["volume"].astype(float)
    mu = v.rolling(window).mean()
    sd = v.rolling(window).std()
    return ((v - mu) / sd).rename(f"volume_z_{window}")


def obv(df: pd.DataFrame) -> pd.Series:
    """On-balance volume. Cumulative; shift-safe (uses prior close to decide sign)."""
    require_columns(df, ["close", "volume"])
    direction = np.sign(df["close"].astype(float).diff()).fillna(0.0)
    return (direction * df["volume"].astype(float)).cumsum().rename("obv")
