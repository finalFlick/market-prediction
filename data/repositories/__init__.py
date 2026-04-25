"""Repository pattern over the DuckDB tables defined in `data/schema.sql`."""

from data.repositories.backtests_repo import BacktestRecord, BacktestsRepo
from data.repositories.signals_repo import SignalRecord, SignalsRepo
from data.repositories.strategies_repo import StrategiesRepo, StrategyRecord
from data.repositories.trades_repo import TradeRecord, TradesRepo

__all__ = [
    "BacktestRecord",
    "BacktestsRepo",
    "SignalRecord",
    "SignalsRepo",
    "StrategiesRepo",
    "StrategyRecord",
    "TradeRecord",
    "TradesRepo",
]
