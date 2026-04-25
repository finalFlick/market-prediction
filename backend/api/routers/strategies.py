"""GET /api/strategies — registered strategies and current status."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.api.deps import strategies_repo
from data.repositories import StrategiesRepo

router = APIRouter()
StrategiesRepoDep = Annotated[StrategiesRepo, Depends(strategies_repo)]


class StrategyOut(BaseModel):
    strategy_id: str
    name: str
    universe: list[str]
    timeframe: str
    status: str
    config_path: str | None = None
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=list[StrategyOut])
def list_strategies(repo: StrategiesRepoDep) -> list[StrategyOut]:
    return [StrategyOut(**s.model_dump()) for s in repo.list()]


@router.get("/{strategy_id}", response_model=StrategyOut)
def get_strategy(strategy_id: str, repo: StrategiesRepoDep) -> StrategyOut:
    record = repo.get(strategy_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"strategy {strategy_id} not found")
    return StrategyOut(**record.model_dump())
