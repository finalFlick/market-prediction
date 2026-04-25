"""Position sizing utilities.

Volatility-targeted sizing converts a target weight into a quantity that
delivers a constant expected portfolio volatility regardless of regime.
"""

from __future__ import annotations

import numpy as np


def vol_targeted_quantity(
    *,
    target_weight: float,
    equity: float,
    price: float,
    realized_vol: float,
    target_annual_vol: float,
    bars_per_year: int = 24 * 365,
) -> float:
    """Return signed quantity to hold for the given target weight.

    `realized_vol` is the per-bar stdev of log returns. `target_annual_vol` is
    the annualized volatility we want the position to contribute when held at
    full weight (|target_weight|=1).
    """
    if equity <= 0 or price <= 0:
        return 0.0
    if realized_vol <= 0 or not np.isfinite(realized_vol):
        return 0.0

    annualized = realized_vol * np.sqrt(bars_per_year)
    scale = target_annual_vol / annualized if annualized > 0 else 0.0
    notional = target_weight * equity * scale
    return notional / price


def clip_quantity_to_min_notional(quantity: float, price: float, min_notional: float) -> float:
    """Zero out positions smaller than `min_notional` to avoid dust orders."""
    if abs(quantity) * price < min_notional:
        return 0.0
    return quantity
