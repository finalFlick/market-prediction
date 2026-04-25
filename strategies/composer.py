"""Combine multiple strategies' target weights into a single target portfolio.

Default policy: equal-volatility-contribution weighting across strategies.
Recompute the per-strategy multiplier on each call so the blend adapts to
regime changes.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping

from risk.types import TargetPosition


def equal_vol_blend(
    weights_by_strategy: Mapping[str, list[TargetPosition]],
    realized_vol: Mapping[str, float],
) -> list[TargetPosition]:
    """Blend per-strategy targets weighted by inverse strategy volatility.

    Strategy volatility is approximated as the gross weight times the average
    underlying vol. This is a placeholder — replace with a covariance-aware
    optimizer when more than ~3 live strategies are running.
    """
    if not weights_by_strategy:
        return []

    inv_vol: dict[str, float] = {}
    for name, targets in weights_by_strategy.items():
        gross = sum(abs(t.weight) for t in targets) or 1.0
        avg_vol = (
            sum(abs(t.weight) * realized_vol.get(t.symbol, 1.0) for t in targets) / gross
        )
        inv_vol[name] = 1.0 / avg_vol if avg_vol > 0 else 0.0

    total = sum(inv_vol.values()) or 1.0
    multiplier = {name: inv_vol[name] / total for name in inv_vol}

    blended: dict[str, float] = defaultdict(float)
    for name, targets in weights_by_strategy.items():
        m = multiplier[name]
        for t in targets:
            blended[t.symbol] += m * t.weight

    blended = {s: max(-1.0, min(1.0, w)) for s, w in blended.items()}
    return [TargetPosition(symbol=s, weight=w) for s, w in blended.items()]
