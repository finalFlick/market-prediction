"""Binance broker adapter (USD-M perps + spot).

Skeleton only. The full adapter wires `python-binance` for REST + websocket,
maintains client-id idempotency, and reconciles positions on every event.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

from execution.brokers.base import Broker, Fill
from monitoring.logger import get_logger
from risk.types import Order, Position

log = get_logger(__name__)


class BinanceBroker(Broker):
    name = "binance"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_secret: str | None = None,
        testnet: bool | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("BINANCE_API_KEY", "")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET", "")
        env_testnet = os.getenv("BINANCE_TESTNET", "true").lower() == "true"
        self.testnet = env_testnet if testnet is None else testnet
        if not self.api_key or not self.api_secret:
            log.warning("binance.no_keys", testnet=self.testnet)

    async def place_order(self, order: Order) -> str:
        log.info("binance.place_order", **order.model_dump(mode="json"), testnet=self.testnet)
        raise NotImplementedError(
            "BinanceBroker.place_order: implement via python-binance "
            "AsyncClient.create_order with newClientOrderId=order.client_id."
        )

    async def cancel_order(self, exchange_order_id: str) -> None:
        log.info("binance.cancel", id=exchange_order_id)
        raise NotImplementedError("BinanceBroker.cancel_order")

    async def get_positions(self) -> dict[str, Position]:
        raise NotImplementedError("BinanceBroker.get_positions")

    async def get_balances(self) -> dict[str, float]:
        raise NotImplementedError("BinanceBroker.get_balances")

    async def stream_events(self) -> AsyncIterator[Fill]:
        raise NotImplementedError("BinanceBroker.stream_events")
        yield  # pragma: no cover
