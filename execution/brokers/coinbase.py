"""Coinbase Advanced Trade broker adapter."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

from execution.brokers.base import Broker, Fill
from monitoring.logger import get_logger
from risk.types import Order, Position

log = get_logger(__name__)


class CoinbaseBroker(Broker):
    name = "coinbase"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        api_secret: str | None = None,
        sandbox: bool | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("COINBASE_API_KEY", "")
        self.api_secret = api_secret or os.getenv("COINBASE_API_SECRET", "")
        env_sandbox = os.getenv("COINBASE_SANDBOX", "true").lower() == "true"
        self.sandbox = env_sandbox if sandbox is None else sandbox
        if not self.api_key or not self.api_secret:
            log.warning("coinbase.no_keys", sandbox=self.sandbox)

    async def place_order(self, order: Order) -> str:
        log.info("coinbase.place_order", **order.model_dump(mode="json"), sandbox=self.sandbox)
        raise NotImplementedError("CoinbaseBroker.place_order")

    async def cancel_order(self, exchange_order_id: str) -> None:
        log.info("coinbase.cancel", id=exchange_order_id)
        raise NotImplementedError("CoinbaseBroker.cancel_order")

    async def get_positions(self) -> dict[str, Position]:
        raise NotImplementedError("CoinbaseBroker.get_positions")

    async def get_balances(self) -> dict[str, float]:
        raise NotImplementedError("CoinbaseBroker.get_balances")

    async def stream_events(self) -> AsyncIterator[Fill]:
        raise NotImplementedError("CoinbaseBroker.stream_events")
        yield  # pragma: no cover
