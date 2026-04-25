"""Yahoo Finance bars via **yfinance** (no key; best-effort for stocks/ETFs/crypto)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterable
from datetime import UTC, datetime
from typing import Any

import pandas as pd

from data.ingest.base import Ingester
from data.types import Exchange, OHLCVBar, Timeframe
from monitoring.logger import get_logger

log = get_logger(__name__)


def _require_yfinance() -> Any:
    try:
        import yfinance as yf  # noqa: PLC0415
    except ImportError as e:
        msg = (
            "yfinance is required for Yahoo data. "
            "Install: pip install 'trading-lab[public-data]' or pip install yfinance"
        )
        raise ImportError(msg) from e
    return yf


def _tf_to_yf_interval_and_rule(
    tf: Timeframe,
) -> tuple[str, str | None]:
    """Return (yfinance interval, optional pandas resample offset)."""
    m: dict[Timeframe, tuple[str, str | None]] = {
        Timeframe.M1: ("1m", None),
        Timeframe.M5: ("5m", None),
        Timeframe.M15: ("15m", None),
        Timeframe.H1: ("1h", None),
        Timeframe.H4: ("1h", "4h"),
        Timeframe.D1: ("1d", None),
    }
    if tf not in m:
        msg = f"unsupported yfinance mapping for {tf!r}"
        raise ValueError(msg)
    return m[tf]


def _row_to_bar(
    row: pd.Series,
    *,
    sym: str,
    tf: Timeframe,
    ts: pd.Timestamp,
) -> OHLCVBar:
    o, h, low, c = float(row["Open"]), float(row["High"]), float(row["Low"]), float(row["Close"])
    v = float(row.get("Volume", 0) or 0)
    ts_dt = ts.to_pydatetime()
    ts_utc = ts_dt.replace(tzinfo=UTC) if ts_dt.tzinfo is None else ts_dt.astimezone(UTC)
    return OHLCVBar(
        exchange=Exchange.YAHOO,
        symbol=sym,
        timeframe=tf,
        ts=ts_utc,
        open=o,
        high=h,
        low=low,
        close=c,
        volume=v,
        quote_volume=0.0,
    )


class YFinanceIngester(Ingester):
    name = "yfinance"

    def fetch_historical(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: datetime,
        end: datetime,
    ) -> Iterable[OHLCVBar]:
        yf = _require_yfinance()
        yfi, resample = _tf_to_yf_interval_and_rule(timeframe)
        t = yf.Ticker(symbol)
        df: pd.DataFrame = t.history(
            start=start,
            end=end,
            interval=yfi,
            auto_adjust=True,
        )
        if df.empty:
            log.warning("yfinance.empty", symbol=symbol, timeframe=timeframe.value)
            return []
        if resample is not None:
            df = (
                df.resample(resample)
                .agg(
                    {
                        "Open": "first",
                        "High": "max",
                        "Low": "min",
                        "Close": "last",
                        "Volume": "sum",
                    }
                )
                .dropna(how="all")
            )
        out: list[OHLCVBar] = []
        for ts_idx, row in df.iterrows():
            if not isinstance(ts_idx, pd.Timestamp):
                continue
            b = _row_to_bar(
                row,
                sym=symbol,
                tf=timeframe,
                ts=ts_idx,
            )
            if start <= b.ts <= end:
                out.append(b)
        log.info("yfinance.fetch_historical", symbol=symbol, rows=len(out))
        return out

    async def stream_live(
        self,
        symbol: str,
        timeframe: Timeframe,
    ) -> AsyncIterator[OHLCVBar]:
        raise NotImplementedError("YFinanceIngester.stream_live: not implemented for MVP-0")
        yield OHLCVBar(
            exchange=Exchange.YAHOO,
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
