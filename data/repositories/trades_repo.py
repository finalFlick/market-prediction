"""Repository for the `trades` table."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd
from pydantic import BaseModel

from data.db import connect


class TradeRecord(BaseModel):
    trade_id: str
    client_order_id: str
    strategy_id: str | None = None
    exchange: str
    symbol: str
    side: str  # buy / sell
    quantity: float
    price: float
    fee: float = 0.0
    pnl: float | None = None
    venue: str  # backtest | paper | live
    ts: datetime


class TradesRepo:
    def __init__(self, path: str | Path | None = None) -> None:
        self._conn: duckdb.DuckDBPyConnection = connect(path)

    def close(self) -> None:
        self._conn.close()

    def insert(self, record: TradeRecord) -> None:
        self._conn.execute(
            """
            INSERT INTO trades
                (trade_id, client_order_id, strategy_id, exchange, symbol, side,
                 quantity, price, fee, pnl, venue, ts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            [
                record.trade_id,
                record.client_order_id,
                record.strategy_id,
                record.exchange,
                record.symbol,
                record.side,
                record.quantity,
                record.price,
                record.fee,
                record.pnl,
                record.venue,
                record.ts,
            ],
        )

    def insert_many(self, records: list[TradeRecord]) -> int:
        if not records:
            return 0
        rows = [
            (
                r.trade_id,
                r.client_order_id,
                r.strategy_id,
                r.exchange,
                r.symbol,
                r.side,
                r.quantity,
                r.price,
                r.fee,
                r.pnl,
                r.venue,
                r.ts,
            )
            for r in records
        ]
        self._conn.executemany(
            """
            INSERT INTO trades
                (trade_id, client_order_id, strategy_id, exchange, symbol, side,
                 quantity, price, fee, pnl, venue, ts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            rows,
        )
        return len(rows)

    def list(
        self,
        *,
        strategy_id: str | None = None,
        symbol: str | None = None,
        venue: str | None = None,
        limit: int = 500,
    ) -> pd.DataFrame:
        clauses: list[str] = []
        params: list[object] = []
        if strategy_id:
            clauses.append("strategy_id = ?")
            params.append(strategy_id)
        if symbol:
            clauses.append("symbol = ?")
            params.append(symbol.upper())
        if venue:
            clauses.append("venue = ?")
            params.append(venue)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.append(limit)
        query = f"SELECT * FROM trades {where} ORDER BY ts DESC LIMIT ?"
        return self._conn.execute(query, params).df()
