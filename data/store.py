"""DuckDB-backed OHLCV store (the `market_data` table).

Idempotent upserts on `(exchange, symbol, timeframe, ts)`. Reads return a
pandas DataFrame indexed by UTC timestamp and ready for feature pipelines.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import duckdb
import pandas as pd

from data.db import connect, default_path
from data.types import Exchange, OHLCVBar, Timeframe
from monitoring.logger import get_logger

log = get_logger(__name__)


class OHLCVStore:
    """Thin wrapper around DuckDB for the `market_data` table."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else default_path()
        self._conn: duckdb.DuckDBPyConnection = connect(self.path)

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> OHLCVStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def upsert(self, bars: Iterable[OHLCVBar]) -> int:
        rows = [
            (
                b.exchange.value,
                b.symbol,
                b.timeframe.value,
                b.ts,
                b.open,
                b.high,
                b.low,
                b.close,
                b.volume,
                b.quote_volume,
            )
            for b in bars
        ]
        if not rows:
            return 0
        self._conn.executemany(
            """
            INSERT OR REPLACE INTO market_data
                (exchange, symbol, timeframe, ts, open, high, low, close, volume, quote_volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            rows,
        )
        log.info("market_data.upsert", rows=len(rows))
        return len(rows)

    def read(
        self,
        exchange: Exchange,
        symbol: str,
        timeframe: Timeframe,
        *,
        start: pd.Timestamp | None = None,
        end: pd.Timestamp | None = None,
    ) -> pd.DataFrame:
        clauses = ["exchange = ?", "symbol = ?", "timeframe = ?"]
        params: list[object] = [exchange.value, symbol.upper(), timeframe.value]
        if start is not None:
            clauses.append("ts >= ?")
            params.append(start.to_pydatetime())
        if end is not None:
            clauses.append("ts <= ?")
            params.append(end.to_pydatetime())
        query = f"""
            SELECT ts, open, high, low, close, volume, quote_volume
            FROM market_data
            WHERE {" AND ".join(clauses)}
            ORDER BY ts ASC;
        """
        df = self._conn.execute(query, params).df()
        if df.empty:
            return df
        df["ts"] = pd.to_datetime(df["ts"], utc=True)
        return df.set_index("ts")
