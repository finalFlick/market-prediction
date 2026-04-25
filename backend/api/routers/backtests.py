"""GET /api/backtests — backtest runs and headline metrics."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from backend.api.deps import backtests_repo
from data.repositories import BacktestsRepo

router = APIRouter()
BacktestsRepoDep = Annotated[BacktestsRepo, Depends(backtests_repo)]


class BacktestOut(BaseModel):
    run_id: str
    strategy_id: str
    git_commit: str | None
    config_hash: str | None
    started_at: datetime
    finished_at: datetime | None
    sharpe: float | None
    sortino: float | None
    max_drawdown: float | None
    cagr: float | None
    final_equity: float | None
    n_trades: int | None
    artifact_dir: str


@router.get("", response_model=list[BacktestOut])
def list_backtests(
    repo: BacktestsRepoDep,
    strategy_id: str | None = Query(None),
    limit: int = Query(50, ge=1, le=500),
) -> list[BacktestOut]:
    return [BacktestOut(**r.model_dump()) for r in repo.list(strategy_id=strategy_id, limit=limit)]


@router.get("/{run_id}", response_model=BacktestOut)
def get_backtest(run_id: str, repo: BacktestsRepoDep) -> BacktestOut:
    record = repo.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"run {run_id} not found")
    return BacktestOut(**record.model_dump())
