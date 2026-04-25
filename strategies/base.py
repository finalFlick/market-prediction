"""Strategy abstract base class.

A strategy emits *target weights* per symbol. It does NOT place orders or
size positions. The risk engine performs sizing and order construction.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import pandas as pd

from risk.types import TargetPosition


@dataclass(frozen=True)
class MarketState:
    """Point-in-time view passed to a strategy on each step.

    `bars` maps symbol -> OHLCV DataFrame (UTC index, oldest first). Only
    rows with `index <= ts` are present; this is enforced by the runner /
    backtest harness so strategies cannot accidentally peek.
    """

    ts: pd.Timestamp
    bars: dict[str, pd.DataFrame]
    extra: dict[str, object] = field(default_factory=dict)


class Strategy(ABC):
    name: str
    universe: list[str]
    timeframe: str

    @abstractmethod
    def target_positions(self, state: MarketState) -> list[TargetPosition]:
        """Return target weights for each symbol in the universe."""

    def warmup_bars(self) -> int:
        """Minimum number of historical bars the strategy needs before producing signals."""
        return 0
