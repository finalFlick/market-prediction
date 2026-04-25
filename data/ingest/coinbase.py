"""Coinbase Advanced Trade ingester (REST historical + websocket live)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterable
from datetime import datetime

from data.ingest.base import Ingester
from data.types import Exchange, OHLCVBar, Timeframe
from monitoring.logger import get_logger

log = get_logger(__name__)


class CoinbaseIngester(Ingester):
    name = "coinbase"

    def __init__(self, *, sandbox: bool = True) -> None:
        self.sandbox = sandbox

    def fetch_historical(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: datetime,
        end: datetime,
    ) -> Iterable[OHLCVBar]:
        log.info(
            "coinbase.fetch_historical",
            symbol=symbol,
            timeframe=timeframe.value,
            start=start.isoformat(),
            end=end.isoformat(),
            sandbox=self.sandbox,
        )
        raise NotImplementedError(
            "CoinbaseIngester.fetch_historical: implement via coinbase-advanced-py "
            "RESTClient.get_candles, paginate by start/end, normalize to OHLCVBar."
        )

    async def stream_live(
        self,
        symbol: str,
        timeframe: Timeframe,
    ) -> AsyncIterator[OHLCVBar]:
        log.info("coinbase.stream_live", symbol=symbol, timeframe=timeframe.value)
        raise NotImplementedError(
            "CoinbaseIngester.stream_live: subscribe to candles channel, yield "
            "completed bars only."
        )
        yield OHLCVBar(  # pragma: no cover
            exchange=Exchange.COINBASE,
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
