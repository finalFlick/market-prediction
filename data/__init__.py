"""Market-data ingestion, storage, and repositories.

`OHLCVStore` covers the `market_data` table; `data.repositories` exposes
typed access to `signals`, `strategies`, `trades`, and `backtests`.
"""

from data.db import connect, default_path
from data.repositories import (
    BacktestRecord,
    BacktestsRepo,
    SignalRecord,
    SignalsRepo,
    StrategiesRepo,
    StrategyRecord,
    TradeRecord,
    TradesRepo,
)
from data.store import OHLCVStore
from data.types import OHLCVBar

__all__ = [
    "BacktestRecord",
    "BacktestsRepo",
    "OHLCVBar",
    "OHLCVStore",
    "SignalRecord",
    "SignalsRepo",
    "StrategiesRepo",
    "StrategyRecord",
    "TradeRecord",
    "TradesRepo",
    "connect",
    "default_path",
]
