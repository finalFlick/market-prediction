"""Baseline momentum-crossover strategy.

Long when fast EMA > slow EMA by a configurable margin, short on the
opposite. Single-symbol; multi-symbol composition is the composer's job.

This is the reference strategy used to exercise the full pipeline; replace
or augment with a model-driven version once `research/models/train.py`
produces a registered artifact.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from research.features.momentum import ema_crossover
from risk.types import TargetPosition
from strategies.base import MarketState, Strategy


@dataclass
class MomentumXover(Strategy):
    name: str = "momentum_xover"
    universe: list[str] = field(default_factory=lambda: ["BTCUSDT"])
    timeframe: str = "1h"
    fast: int = 12
    slow: int = 26
    threshold: float = 0.001
    long_only: bool = False
    target_weight: float = 0.5

    def warmup_bars(self) -> int:
        return self.slow * 5

    def target_positions(self, state: MarketState) -> list[TargetPosition]:
        out: list[TargetPosition] = []
        for symbol in self.universe:
            df = state.bars.get(symbol)
            if df is None or len(df) < self.warmup_bars():
                out.append(TargetPosition(symbol=symbol, weight=0.0))
                continue
            sig = ema_crossover(df, fast=self.fast, slow=self.slow).iloc[-1]
            if pd.isna(sig):
                weight = 0.0
            elif sig > self.threshold:
                weight = self.target_weight
            elif sig < -self.threshold and not self.long_only:
                weight = -self.target_weight
            else:
                weight = 0.0
            out.append(TargetPosition(symbol=symbol, weight=weight))
        return out
