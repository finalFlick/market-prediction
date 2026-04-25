"""Repository for the `backtests` table."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import duckdb
from pydantic import BaseModel

from data.db import connect


class BacktestRecord(BaseModel):
    run_id: str
    strategy_id: str
    git_commit: str | None = None
    config_hash: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
    sharpe: float | None = None
    sortino: float | None = None
    max_drawdown: float | None = None
    cagr: float | None = None
    final_equity: float | None = None
    n_trades: int | None = None
    artifact_dir: str


class BacktestsRepo:
    def __init__(self, path: str | Path | None = None) -> None:
        self._conn: duckdb.DuckDBPyConnection = connect(path)

    def close(self) -> None:
        self._conn.close()

    def insert(self, record: BacktestRecord) -> None:
        self._conn.execute(
            """
            INSERT OR REPLACE INTO backtests
                (run_id, strategy_id, git_commit, config_hash, started_at, finished_at,
                 sharpe, sortino, max_drawdown, cagr, final_equity, n_trades, artifact_dir)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            [
                record.run_id,
                record.strategy_id,
                record.git_commit,
                record.config_hash,
                record.started_at,
                record.finished_at,
                record.sharpe,
                record.sortino,
                record.max_drawdown,
                record.cagr,
                record.final_equity,
                record.n_trades,
                record.artifact_dir,
            ],
        )

    def list(
        self,
        *,
        strategy_id: str | None = None,
        limit: int = 100,
    ) -> list[BacktestRecord]:
        if strategy_id:
            rows = self._conn.execute(
                "SELECT * FROM backtests WHERE strategy_id = ? ORDER BY started_at DESC LIMIT ?",
                [strategy_id, limit],
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM backtests ORDER BY started_at DESC LIMIT ?", [limit]
            ).fetchall()
        cols = [d[0] for d in self._conn.description]
        return [BacktestRecord(**dict(zip(cols, r, strict=True))) for r in rows]

    def get(self, run_id: str) -> BacktestRecord | None:
        row = self._conn.execute(
            "SELECT * FROM backtests WHERE run_id = ?", [run_id]
        ).fetchone()
        if row is None:
            return None
        cols = [d[0] for d in self._conn.description]
        return BacktestRecord(**dict(zip(cols, row, strict=True)))
