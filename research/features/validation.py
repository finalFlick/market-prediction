"""Anti-leakage validators for the feature pipeline.

If a feature value at time `t` is allowed to depend on data later than `t`,
the entire research process is invalid. These checks catch the common bugs.
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd


def assert_no_lookahead(
    feature_fn: Callable[[pd.DataFrame], pd.Series | pd.DataFrame],
    df: pd.DataFrame,
    *,
    cut: int | None = None,
) -> None:
    """Compute the feature on full and truncated data; rows up to `cut` must match.

    Catches functions that peek at future rows. Choose `cut` >= max lookback.
    """
    if cut is None:
        cut = max(50, len(df) // 2)
    if cut <= 0 or cut >= len(df):
        raise ValueError("cut must be in (0, len(df))")

    full = feature_fn(df)
    head = feature_fn(df.iloc[:cut])

    if isinstance(full, pd.DataFrame):
        full_head = full.iloc[:cut]
        if not full_head.equals(head):
            diffs = (full_head.fillna(0) - head.fillna(0)).abs().sum().sum()
            raise AssertionError(f"look-ahead detected in feature DataFrame; abs diff={diffs}")
        return

    full_head = full.iloc[:cut]
    if not full_head.equals(head):
        diff = (full_head.fillna(0) - head.fillna(0)).abs().sum()
        raise AssertionError(f"look-ahead detected in feature '{full.name}'; abs diff={diff}")


def assert_utc_index(df: pd.DataFrame) -> None:
    if not isinstance(df.index, pd.DatetimeIndex):
        raise AssertionError("DataFrame index must be a DatetimeIndex")
    if df.index.tz is None:
        raise AssertionError("DataFrame index must be timezone-aware (UTC)")
    if str(df.index.tz) != "UTC":
        raise AssertionError(f"DataFrame index must be UTC, got {df.index.tz}")
