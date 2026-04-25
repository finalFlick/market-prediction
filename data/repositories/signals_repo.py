"""Repository for the `signals` table."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import duckdb
from pydantic import BaseModel

from data.db import connect


class SignalRecord(BaseModel):
    signal_id: str
    name: str
    status: str
    timeframe: str
    intuition: str | None = None
    owner: str | None = None
    updated_at: datetime


class SignalsRepo:
    def __init__(self, path: str | Path | None = None) -> None:
        self._conn: duckdb.DuckDBPyConnection = connect(path)

    def close(self) -> None:
        self._conn.close()

    def upsert(self, record: SignalRecord) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO signals
                (signal_id, name, status, timeframe, intuition, owner, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            [
                record.signal_id,
                record.name,
                record.status,
                record.timeframe,
                record.intuition,
                record.owner,
                record.updated_at,
            ],
        )

    def list(self, *, status: str | None = None) -> list[SignalRecord]:
        if status:
            rows = self._conn.execute(
                "SELECT * FROM signals WHERE status = ? ORDER BY signal_id ASC", [status]
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM signals ORDER BY signal_id ASC"
            ).fetchall()
        cols = [d[0] for d in self._conn.description]
        return [SignalRecord(**dict(zip(cols, r, strict=True))) for r in rows]

    def update_status(self, signal_id: str, status: str) -> None:
        self._conn.execute(
            "UPDATE signals SET status = ?, updated_at = ? WHERE signal_id = ?",
            [status, datetime.now(tz=UTC), signal_id],
        )
