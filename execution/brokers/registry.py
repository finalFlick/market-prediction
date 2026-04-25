"""Broker registry with a default lock on live adapter registration."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import yaml

from execution.brokers.base import Broker

_RUNTIME_CONFIG = Path("configs/runtime.yaml")


class LiveAdapterRegistrationForbidden(Exception):  # noqa: N818
    """Raised when live adapter registration is attempted while locked."""

    def __init__(self, broker: str, reason: str) -> None:
        super().__init__(f"[{broker}] {reason}")
        self.broker = broker
        self.reason = reason


def _default_unlocked_provider() -> bool:
    """Read the MVP-0 live registration lock from runtime config.

    Design note: this reads `configs/runtime.yaml` at MVP-0. The v1.1 design
    migrates this unlock signal to `config_kv` after pre-live gate approval.
    """
    if not _RUNTIME_CONFIG.exists():
        return False
    payload = yaml.safe_load(_RUNTIME_CONFIG.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        return False
    return bool(payload.get("live_adapters_unlocked", False))


class LiveBrokerRegistry:
    """Registry for broker adapters with explicit lock on live adapters."""

    def __init__(
        self, *, unlocked_provider: Callable[[], bool] = _default_unlocked_provider
    ) -> None:
        self._unlocked_provider = unlocked_provider
        self._brokers: dict[str, Broker] = {}

    @property
    def brokers(self) -> dict[str, Broker]:
        return dict(self._brokers)

    def register(self, broker: Broker) -> None:
        if _is_live_broker(broker) and not self._unlocked_provider():
            raise LiveAdapterRegistrationForbidden(
                broker=broker.name,
                reason="pre_live_gate_not_passed_or_flag_off",
            )
        self._brokers[broker.name] = broker


def _is_live_broker(broker: Broker) -> bool:
    return broker.name in {"binance", "coinbase"}
