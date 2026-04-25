"""Binance ingester (REST historical + websocket live).

The full implementation belongs in Milestone 1 of `TODO.md`. This file
defines the public surface and a working stub that respects the contract so
downstream code can be developed and tested with `MockBinance` fixtures.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterable
from datetime import datetime

from data.ingest.base import Ingester
from data.types import Exchange, OHLCVBar, Timeframe
from monitoring.logger import get_logger

log = get_logger(__name__)


class BinanceIngester(Ingester):
    name = "binance"

    def __init__(self, *, testnet: bool = True) -> None:
        self.testnet = testnet

    def fetch_historical(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: datetime,
        end: datetime,
    ) -> Iterable[OHLCVBar]:
        log.info(
            "binance.fetch_historical",
            symbol=symbol,
            timeframe=timeframe.value,
            start=start.isoformat(),
            end=end.isoformat(),
            testnet=self.testnet,
        )
        raise NotImplementedError(
            "BinanceIngester.fetch_historical: implement via python-binance "
            "client.get_historical_klines, paginate, normalize to OHLCVBar."
        )

    async def stream_live(
        self,
        symbol: str,
        timeframe: Timeframe,
    ) -> AsyncIterator[OHLCVBar]:
        log.info("binance.stream_live", symbol=symbol, timeframe=timeframe.value)
        raise NotImplementedError(
            "BinanceIngester.stream_live: connect to wss kline stream, yield only "
            "closed bars (kline 'x' == True)."
        )
        # Unreachable; satisfies type checker for AsyncIterator.
        yield OHLCVBar(  # pragma: no cover
            exchange=Exchange.BINANCE,
            symbol=symbol,
            timeframe=timeframe,
            ts=datetime.now(),
            open=0.0,
            high=0.0,
            low=0.0,
            close=0.0,
            volume=0.0,
            quote_volume=0.0,
        )
        await asyncio.sleep(0)  # pragma: no cover
