"""In-process paper broker.

Fills market orders against the next observed price using the project cost
model. Used for paper trading and as the default broker for backtests run
through the runner (e.g. shadow paper alongside live).
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import uuid4

from execution.brokers.base import Broker, Fill
from monitoring.logger import get_logger
from risk.types import Order, OrderSide, Position

log = get_logger(__name__)


class PaperBroker(Broker):
    name = "paper"

    def __init__(
        self,
        *,
        starting_cash: float = 100_000.0,
        slippage_bps: float = 5.0,
        fee_bps: float = 10.0,
    ) -> None:
        self.cash = starting_cash
        self.slippage_bps = slippage_bps
        self.fee_bps = fee_bps
        self._positions: dict[str, Position] = {}
        self._marks: dict[str, float] = {}
        self._fills: asyncio.Queue[Fill] = asyncio.Queue()
        self._orders_by_id: dict[str, Order] = {}

    def update_mark(self, symbol: str, price: float) -> None:
        if price <= 0:
            raise ValueError("price must be positive")
        self._marks[symbol] = price

    async def place_order(self, order: Order) -> str:
        mark = self._marks.get(order.symbol)
        if mark is None:
            raise RuntimeError(f"no mark for {order.symbol}; call update_mark first")

        slip = self.slippage_bps / 1e4
        fee_rate = self.fee_bps / 1e4
        if order.side == OrderSide.BUY:
            price = mark * (1 + slip)
            cost = price * order.quantity
            fee = cost * fee_rate
            self.cash -= cost + fee
            self._apply_fill(order.symbol, +order.quantity, price)
        else:
            price = mark * (1 - slip)
            proceeds = price * order.quantity
            fee = proceeds * fee_rate
            self.cash += proceeds - fee
            self._apply_fill(order.symbol, -order.quantity, price)

        exchange_id = f"paper-{uuid4().hex[:10]}"
        self._orders_by_id[exchange_id] = order
        fill = Fill(
            client_id=order.client_id,
            exchange_order_id=exchange_id,
            symbol=order.symbol,
            side=order.side.value,
            quantity=order.quantity,
            price=price,
            fee=fee,
            ts=datetime.now(tz=UTC),
        )
        await self._fills.put(fill)
        log.info("paper.fill", **fill.model_dump(mode="json"))
        return exchange_id

    async def cancel_order(self, exchange_order_id: str) -> None:
        # Paper broker fills synchronously, so cancel is a no-op.
        self._orders_by_id.pop(exchange_order_id, None)

    async def get_positions(self) -> dict[str, Position]:
        return dict(self._positions)

    async def get_balances(self) -> dict[str, float]:
        return {"USD": self.cash}

    async def stream_events(self) -> AsyncIterator[Fill]:
        while True:
            yield await self._fills.get()

    def _apply_fill(self, symbol: str, signed_qty: float, price: float) -> None:
        pos = self._positions.get(symbol)
        if pos is None:
            self._positions[symbol] = Position(symbol=symbol, quantity=signed_qty, avg_price=price)
            return
        new_qty = pos.quantity + signed_qty
        if new_qty == 0:
            self._positions.pop(symbol)
            return
        if (pos.quantity > 0 and signed_qty > 0) or (pos.quantity < 0 and signed_qty < 0):
            new_avg = (pos.quantity * pos.avg_price + signed_qty * price) / new_qty
        else:
            new_avg = pos.avg_price
        self._positions[symbol] = Position(symbol=symbol, quantity=new_qty, avg_price=new_avg)
