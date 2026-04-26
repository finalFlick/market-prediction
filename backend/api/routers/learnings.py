"""GET /api/learnings — lever scoreboard and run comparison (MVP-0)."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query
from pydantic import BaseModel

from data.db import connect

router = APIRouter()


class ScoreboardRow(BaseModel):
    level: str
    key: str
    score: float
    weight: float
    last_run_id: str | None
    updated_at: datetime


class RunCompareRow(BaseModel):
    run_id: str
    run_type: str
    mode: str
    status: str
    config_hash: str | None
    git_commit: str | None
    started_at: datetime | None
    finished_at: datetime | None
    sharpe: float | None
    max_drawdown: float | None
    cagr: float | None
    n_trades: int | None
    artifact_dir: str | None


@router.get("/scoreboard", response_model=list[ScoreboardRow])
def scoreboard(limit: int = Query(100, ge=1, le=500)) -> list[ScoreboardRow]:
    conn = connect()
    rows = conn.execute(
        """
        SELECT level, key, score, weight, last_run_id, updated_at
        FROM scoreboard ORDER BY level, key LIMIT ?
        """,
        [limit],
    ).fetchall()
    conn.close()
    return [
        ScoreboardRow(
            level=r[0],
            key=r[1],
            score=r[2],
            weight=r[3],
            last_run_id=r[4],
            updated_at=r[5],
        )
        for r in rows
    ]


@router.get("/compare", response_model=list[RunCompareRow])
def compare_runs(
    ids: str = Query(..., description="Comma-separated run_ids, e.g. run-a,run-b"),
) -> list[RunCompareRow]:
    """Return side-by-side run summaries for the given run IDs."""
    run_ids = [i.strip() for i in ids.split(",") if i.strip()]
    if not run_ids:
        return []

    conn = connect()
    placeholders = ", ".join(["?"] * len(run_ids))
    runs_rows = conn.execute(
        f"""
        SELECT r.run_id, r.run_type, r.mode, r.status, r.config_hash, r.git_commit,
               r.started_at, r.finished_at, r.artifact_dir,
               b.sharpe, b.max_drawdown, b.cagr, b.n_trades
        FROM runs r
        LEFT JOIN backtests b ON r.run_id = b.run_id
        WHERE r.run_id IN ({placeholders})
        ORDER BY r.run_id
        """,
        run_ids,
    ).fetchall()
    conn.close()

    return [
        RunCompareRow(
            run_id=row[0],
            run_type=row[1],
            mode=row[2],
            status=row[3],
            config_hash=row[4],
            git_commit=row[5],
            started_at=row[6],
            finished_at=row[7],
            artifact_dir=row[8],
            sharpe=row[9],
            max_drawdown=row[10],
            cagr=row[11],
            n_trades=row[12],
        )
        for row in runs_rows
    ]
