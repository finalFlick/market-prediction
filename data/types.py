"""Cross-module data contracts."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class Exchange(StrEnum):
    BINANCE = "binance"
    COINBASE = "coinbase"
    YAHOO = "yahoo"


class Timeframe(StrEnum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"


class OHLCVBar(BaseModel):
    """A single OHLCV bar normalized across exchanges.

    The (exchange, symbol, timeframe, ts) tuple is the unique key.
    Timestamps are bar OPEN time, always UTC and timezone-aware.
    """

    exchange: Exchange
    symbol: str
    timeframe: Timeframe
    ts: datetime
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0)
    quote_volume: float = Field(ge=0)

    @field_validator("ts")
    @classmethod
    def _ts_must_be_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware UTC")
        return v

    @field_validator("symbol")
    @classmethod
    def _symbol_upper(cls, v: str) -> str:
        return v.upper()
