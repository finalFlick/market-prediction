"""Feature protocol and convenience helpers."""

from __future__ import annotations

from typing import Protocol

import pandas as pd


class Feature(Protocol):
    """Stateless transformation from OHLCV to a feature column or DataFrame."""

    name: str
    lookback: int  # bars of history needed to produce a non-NaN value

    def __call__(self, df: pd.DataFrame) -> pd.Series | pd.DataFrame: ...


def require_columns(df: pd.DataFrame, cols: list[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"DataFrame is missing required columns: {missing}")
