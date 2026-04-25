"""Prediction targets used to train signal models.

All labels are computed *after* features are computed and use only future
information relative to the feature timestamp. The shift relationship is
documented per function so that the leakage check in
`research.features.validation` can verify it.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def forward_log_return(close: pd.Series, horizon: int) -> pd.Series:
    """Log-return from bar `t` close to bar `t+horizon` close.

    The returned series is indexed at `t` (the *decision* time). It will be
    NaN for the last `horizon` bars where the future close is unknown.
    """
    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    log_close = np.log(close.astype(float))
    return (log_close.shift(-horizon) - log_close).rename(f"label_logret_{horizon}")


def triple_barrier(
    close: pd.Series,
    *,
    upper: float,
    lower: float,
    max_horizon: int,
) -> pd.Series:
    """Triple-barrier label: +1 if upper hit first, -1 if lower, 0 if timeout.

    `upper` and `lower` are fractional thresholds (e.g. 0.01 = +1%). Returned
    series is indexed at the decision time `t`.
    """
    if upper <= 0 or lower <= 0:
        raise ValueError("upper and lower must be positive fractions")
    if max_horizon < 1:
        raise ValueError("max_horizon must be >= 1")

    arr = close.astype(float).to_numpy()
    n = arr.size
    out = np.zeros(n, dtype=np.int8)
    for i in range(n):
        end = min(i + max_horizon, n - 1)
        if end <= i:
            out[i] = 0
            continue
        window = arr[i + 1 : end + 1] / arr[i] - 1.0
        up_hits = np.where(window >= upper)[0]
        down_hits = np.where(window <= -lower)[0]
        first_up = up_hits[0] if up_hits.size else np.iinfo(np.int64).max
        first_down = down_hits[0] if down_hits.size else np.iinfo(np.int64).max
        if first_up == first_down == np.iinfo(np.int64).max:
            out[i] = 0
        elif first_up < first_down:
            out[i] = 1
        else:
            out[i] = -1
    label = pd.Series(out, index=close.index, name="label_triple_barrier")
    label.iloc[-max_horizon:] = 0
    return label
