"""Cross-module data contracts for risk and execution."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"


class TimeInForce(StrEnum):
    GTC = "gtc"
    IOC = "ioc"
    FOK = "fok"


class TargetPosition(BaseModel):
    """Strategy-emitted target weight for a symbol."""

    symbol: str
    weight: float = Field(ge=-1.0, le=1.0)


class Order(BaseModel):
    """Risk-approved order ready for an execution adapter."""

    client_id: str = Field(default_factory=lambda: str(uuid4()))
    symbol: str
    side: OrderSide
    quantity: float = Field(gt=0)
    order_type: OrderType = OrderType.MARKET
    limit_price: float | None = None
    time_in_force: TimeInForce = TimeInForce.GTC
    reduce_only: bool = False


class Position(BaseModel):
    symbol: str
    quantity: float
    avg_price: float = Field(ge=0)

    @property
    def is_flat(self) -> bool:
        return self.quantity == 0.0


class Portfolio(BaseModel):
    """Snapshot of the trading account at a point in time."""

    ts: datetime
    cash: float
    positions: dict[str, Position] = Field(default_factory=dict)
    realized_pnl_today: float = 0.0
    high_water_mark: float = 0.0

    def equity(self, marks: dict[str, float]) -> float:
        """Total equity = cash + sum(qty * mark)."""
        eq = self.cash
        for sym, pos in self.positions.items():
            mark = marks.get(sym, pos.avg_price)
            eq += pos.quantity * mark
        return eq

    def gross_exposure(self, marks: dict[str, float]) -> float:
        return sum(abs(p.quantity) * marks.get(s, p.avg_price) for s, p in self.positions.items())

    def net_exposure(self, marks: dict[str, float]) -> float:
        return sum(p.quantity * marks.get(s, p.avg_price) for s, p in self.positions.items())
