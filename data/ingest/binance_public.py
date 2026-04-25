"""Binance public REST klines (no API key; ``GET /api/v3/klines``)."""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator, Iterable
from datetime import UTC, datetime
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from data.ingest.base import Ingester
from data.types import Exchange, OHLCVBar, Timeframe
from monitoring.logger import get_logger

log = get_logger(__name__)

_DEFAULT_SPOT = "https://api.binance.com"
_BINANCE_MAX_KLINES = 1000


def _binance_klines_url() -> str:
    base = (os.getenv("BINANCE_PUBLIC_REST_BASE") or _DEFAULT_SPOT).rstrip("/")
    return f"{base}/api/v3/klines"


def _timeframe_to_interval(tf: Timeframe) -> str:
    m = {
        Timeframe.M1: "1m",
        Timeframe.M5: "5m",
        Timeframe.M15: "15m",
        Timeframe.H1: "1h",
        Timeframe.H4: "4h",
        Timeframe.D1: "1d",
    }
    if tf not in m:
        msg = f"unsupported Binance interval for {tf!r}"
        raise ValueError(msg)
    return m[tf]


def _row_to_bar(row: list[Any], *, symbol: str, tf: Timeframe, sym_upper: str) -> OHLCVBar:
    open_ms = int(row[0])
    o, h, low, c = float(row[1]), float(row[2]), float(row[3]), float(row[4])
    vol = float(row[5])
    quote_volume_field = 7  # kline field index for quote-asset volume
    qv = float(row[quote_volume_field]) if len(row) > quote_volume_field else 0.0
    ts = datetime.fromtimestamp(open_ms / 1000.0, tz=UTC)
    return OHLCVBar(
        exchange=Exchange.BINANCE,
        symbol=sym_upper,
        timeframe=tf,
        ts=ts,
        open=o,
        high=h,
        low=low,
        close=c,
        volume=vol,
        quote_volume=qv,
    )


class BinancePublicIngester(Ingester):
    """Public market data only; no ``apiKey`` on requests."""

    name = "binance_public"

    @retry(
        wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
        stop=stop_after_attempt(4),
    )
    def _get_klines(
        self,
        *,
        symbol: str,
        interval: str,
        start_ms: int | None,
        end_ms: int | None,
        limit: int = _BINANCE_MAX_KLINES,
    ) -> list[list[Any]]:
        params: dict[str, str | int] = {
            "symbol": symbol.upper().replace("-", ""),
            "interval": interval,
            "limit": limit,
        }
        if start_ms is not None:
            params["startTime"] = start_ms
        if end_ms is not None:
            params["endTime"] = end_ms
        with httpx.Client(timeout=30.0) as client:
            r = client.get(_binance_klines_url(), params=params)
            r.raise_for_status()
            data = r.json()
        if not isinstance(data, list):
            msg = f"unexpected Binance klines response: {data!r}"
            raise TypeError(msg)
        return data

    def fetch_historical(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: datetime,
        end: datetime,
    ) -> Iterable[OHLCVBar]:
        sym = symbol.upper().replace("-", "")
        interval = _timeframe_to_interval(timeframe)
        start_ms = int(start.timestamp() * 1000)
        end_ms = int(end.timestamp() * 1000)
        raw: list[list[Any]] = []
        cur = start_ms
        while cur < end_ms:
            batch = self._get_klines(
                symbol=sym,
                interval=interval,
                start_ms=cur,
                end_ms=end_ms,
                limit=_BINANCE_MAX_KLINES,
            )
            if not batch:
                break
            raw.extend(batch)
            last_open = int(batch[-1][0])
            nxt = last_open + 1
            if nxt <= cur:
                break
            cur = nxt
            if len(batch) < _BINANCE_MAX_KLINES:
                break
        by_ts: dict[datetime, OHLCVBar] = {}
        for row in raw:
            bar = _row_to_bar(row, symbol=symbol, tf=timeframe, sym_upper=sym)
            if bar.ts < start or bar.ts > end:
                continue
            by_ts[bar.ts] = bar
        out = sorted(by_ts.values(), key=lambda b: b.ts)
        log.info("binance_public.fetch_historical", symbol=sym, rows=len(out))
        return out

    async def stream_live(
        self,
        symbol: str,
        timeframe: Timeframe,
    ) -> AsyncIterator[OHLCVBar]:
        raise NotImplementedError(
            "BinancePublicIngester.stream_live: use fetch_historical for MVP-0; "
            "or subscribe to wss with a separate adapter."
        )
        yield OHLCVBar(
            exchange=Exchange.BINANCE,
            symbol=symbol.upper(),
            timeframe=timeframe,
            ts=datetime.now(tz=UTC),
            open=1.0,
            high=1.0,
            low=1.0,
            close=1.0,
            volume=0.0,
            quote_volume=0.0,
        )
        await asyncio.sleep(0)  # pragma: no cover
