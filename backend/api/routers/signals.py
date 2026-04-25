"""GET /api/signals — signal backlog and lifecycle status."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from backend.api.deps import signals_repo
from data.repositories import SignalsRepo

router = APIRouter()
SignalsRepoDep = Annotated[SignalsRepo, Depends(signals_repo)]

_ALLOWED_STATUS = {"hypothesis", "research", "backtest", "paper", "live", "retired"}


class SignalOut(BaseModel):
    signal_id: str
    name: str
    status: str
    timeframe: str
    intuition: str | None = None
    owner: str | None = None
    updated_at: datetime


@router.get("", response_model=list[SignalOut])
def list_signals(
    repo: SignalsRepoDep,
    status: str | None = Query(None),
) -> list[SignalOut]:
    if status is not None and status not in _ALLOWED_STATUS:
        return []
    return [SignalOut(**s.model_dump()) for s in repo.list(status=status)]
