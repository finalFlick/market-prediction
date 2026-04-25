"""Coinbase Exchange public REST candles (no API key)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterable
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from data.ingest.base import Ingester
from data.types import Exchange, OHLCVBar, Timeframe
from monitoring.logger import get_logger

log = get_logger(__name__)

_CANDLES_TMPL = "https://api.exchange.coinbase.com/products/{product_id}/candles"


def _product_id(raw: str) -> str:
    s = raw.strip().upper()
    if "-" in s:
        return s
    for q in ("USDT", "USD"):
        if s.endswith(q) and len(s) > len(q):
            return f"{s[: -len(q)]}-{q}"
    return f"{s}-USD"


def _granularity_seconds(tf: Timeframe) -> int:
    m = {
        Timeframe.M1: 60,
        Timeframe.M5: 300,
        Timeframe.M15: 900,
        Timeframe.H1: 3600,
        Timeframe.H4: 14_400,
        Timeframe.D1: 86_400,
    }
    if tf not in m:
        msg = f"unsupported Coinbase granularity for {tf!r}"
        raise ValueError(msg)
    return m[tf]


def _bar_from_row(row: list[Any], *, product_id: str, tf: Timeframe) -> OHLCVBar:
    # [ time, low, high, open, volume ] — no close in public schema; use open as close.
    t_sec, low, high, o, vol = (
        int(row[0]),
        float(row[1]),
        float(row[2]),
        float(row[3]),
        float(row[4]),
    )
    ts = datetime.fromtimestamp(t_sec, tz=UTC)
    c = o
    return OHLCVBar(
        exchange=Exchange.COINBASE,
        symbol=product_id.upper(),
        timeframe=tf,
        ts=ts,
        open=o,
        high=high,
        low=low,
        close=c,
        volume=vol,
        quote_volume=0.0,
    )


class CoinbasePublicIngester(Ingester):
    """Public ``GET /products/{id}/candles``; no auth header."""

    name = "coinbase_public"

    @retry(
        wait=wait_exponential(multiplier=0.5, min=0.5, max=8),
        stop=stop_after_attempt(4),
    )
    def _get_candles(
        self,
        product_id: str,
        gran: int,
        start_iso: str,
        end_iso: str,
    ) -> list[list[Any]]:
        url = _CANDLES_TMPL.format(product_id=product_id)
        params: dict[str, str | int] = {
            "granularity": gran,
            "start": start_iso,
            "end": end_iso,
        }
        with httpx.Client(timeout=30.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        if not isinstance(data, list):
            msg = f"unexpected Coinbase candles response: {data!r}"
            raise TypeError(msg)
        return data

    def fetch_historical(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: datetime,
        end: datetime,
    ) -> Iterable[OHLCVBar]:
        product_id = _product_id(symbol)
        gran = _granularity_seconds(timeframe)
        out: list[OHLCVBar] = []
        # Coinbase returns at most ~300 candles per request; chunk by 300 * granularity.
        step = timedelta(seconds=300 * gran)
        cur = start
        while cur < end:
            nxt = min(end, cur + step)
            batch = self._get_candles(
                product_id,
                gran,
                cur.replace(microsecond=0).isoformat(),
                nxt.replace(microsecond=0).isoformat(),
            )
            for row in batch:
                b = _bar_from_row(row, product_id=product_id, tf=timeframe)
                if b.ts >= start and b.ts <= end:
                    out.append(b)
            cur = nxt
        out.sort(key=lambda b: b.ts)
        seen: set[datetime] = set()
        deduped: list[OHLCVBar] = []
        for b in out:
            if b.ts in seen:
                continue
            seen.add(b.ts)
            deduped.append(b)
        log.info("coinbase_public.fetch_historical", product=product_id, rows=len(deduped))
        return deduped

    async def stream_live(
        self,
        symbol: str,
        timeframe: Timeframe,
    ) -> AsyncIterator[OHLCVBar]:
        raise NotImplementedError("CoinbasePublicIngester.stream_live: not implemented for MVP-0")
        yield OHLCVBar(
            exchange=Exchange.COINBASE,
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
