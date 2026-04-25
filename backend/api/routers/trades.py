"""GET /api/trades — recent trades, filterable by strategy / symbol / venue."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from backend.api.deps import trades_repo
from data.repositories import TradesRepo

router = APIRouter()
TradesRepoDep = Annotated[TradesRepo, Depends(trades_repo)]


class TradeOut(BaseModel):
    trade_id: str
    client_order_id: str
    strategy_id: str | None
    exchange: str
    symbol: str
    side: str
    quantity: float
    price: float
    fee: float
    pnl: float | None
    venue: str
    ts: str


@router.get("", response_model=list[TradeOut])
def list_trades(
    repo: TradesRepoDep,
    strategy_id: str | None = Query(None),
    symbol: str | None = Query(None),
    venue: str | None = Query(None, pattern="^(backtest|paper|live)$"),
    limit: int = Query(200, ge=1, le=5000),
) -> list[TradeOut]:
    df = repo.list(strategy_id=strategy_id, symbol=symbol, venue=venue, limit=limit)
    if df.empty:
        return []
    df = df.copy()
    df["ts"] = df["ts"].astype("string")
    return [TradeOut(**row) for row in df.to_dict(orient="records")]
