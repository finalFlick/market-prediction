"""Abstract Broker interface every adapter implements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from datetime import datetime

from pydantic import BaseModel, Field

from risk.types import Order, Position


class Fill(BaseModel):
    """A confirmed fill from the exchange."""

    client_id: str
    exchange_order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    fee: float = 0.0
    ts: datetime
    extra: dict[str, str] = Field(default_factory=dict)


class Broker(ABC):
    """Minimal cross-exchange order interface."""

    name: str

    @abstractmethod
    async def place_order(self, order: Order) -> str:
        """Submit an order. Returns the exchange-side order id. Idempotent on `client_id`."""

    @abstractmethod
    async def cancel_order(self, exchange_order_id: str) -> None: ...

    @abstractmethod
    async def get_positions(self) -> dict[str, Position]: ...

    @abstractmethod
    async def get_balances(self) -> dict[str, float]: ...

    @abstractmethod
    def stream_events(self) -> AsyncIterator[Fill]:
        """Yield fills (and optionally other lifecycle events) in real time."""
