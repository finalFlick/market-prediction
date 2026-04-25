"""Repository for the `strategies` table."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import duckdb
from pydantic import BaseModel

from data.db import connect


class StrategyRecord(BaseModel):
    strategy_id: str
    name: str
    universe: list[str]
    timeframe: str
    status: str
    config_path: str | None = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict[str, object]) -> StrategyRecord:
        universe_str = str(row.get("universe") or "")
        return cls(
            strategy_id=str(row["strategy_id"]),
            name=str(row["name"]),
            universe=[s for s in universe_str.split(",") if s],
            timeframe=str(row["timeframe"]),
            status=str(row["status"]),
            config_path=row.get("config_path"),  # type: ignore[arg-type]
            created_at=row["created_at"],  # type: ignore[arg-type]
            updated_at=row["updated_at"],  # type: ignore[arg-type]
        )


class StrategiesRepo:
    def __init__(self, path: str | Path | None = None) -> None:
        self._conn: duckdb.DuckDBPyConnection = connect(path)

    def close(self) -> None:
        self._conn.close()

    def upsert(self, record: StrategyRecord) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO strategies
                (
                    strategy_id, name, universe, timeframe,
                    status, config_path, created_at, updated_at
                )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            [
                record.strategy_id,
                record.name,
                ",".join(record.universe),
                record.timeframe,
                record.status,
                record.config_path,
                record.created_at,
                record.updated_at,
            ],
        )

    def list(self) -> list[StrategyRecord]:
        rows = self._conn.execute(
            "SELECT * FROM strategies ORDER BY name ASC"
        ).fetchall()
        cols = [d[0] for d in self._conn.description]
        return [StrategyRecord.from_row(dict(zip(cols, r, strict=True))) for r in rows]

    def get(self, strategy_id: str) -> StrategyRecord | None:
        row = self._conn.execute(
            "SELECT * FROM strategies WHERE strategy_id = ?", [strategy_id]
        ).fetchone()
        if row is None:
            return None
        cols = [d[0] for d in self._conn.description]
        return StrategyRecord.from_row(dict(zip(cols, row, strict=True)))
