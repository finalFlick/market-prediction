"""POC 2: only risk-approved path can place orders (toy gated broker)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class RejectReason:
    BYPASS = "bypass"


@dataclass
class ToyOrder:
    symbol: str
    qty: float


class GatedBroker:
    """Accepts place() only if caller identity is the risk layer."""

    def __init__(self) -> None:
        self.fills: list[ToyOrder] = []

    def place(self, order: ToyOrder, *, caller: str) -> str:
        if caller != "risk_engine":
            raise RuntimeError(RejectReason.BYPASS)
        self.fills.append(order)
        return "ok"


def strategy_emits_order_directly(broker: GatedBroker) -> None:
    """What we want to forbid: strategy → broker without risk."""
    broker.place(ToyOrder("BTC", 1.0), caller="strategy")


def legitimate_path(broker: GatedBroker) -> None:
    """Strategy → risk → broker."""
    raw = ToyOrder("BTC", 1.0)
    _ = raw  # strategy only proposes; risk would validate/size
    approved = ToyOrder("BTC", 0.5)  # after sizing
    broker.place(approved, caller="risk_engine")


def main() -> None:
    b = GatedBroker()
    try:
        strategy_emits_order_directly(b)
    except RuntimeError as e:
        assert str(e) == RejectReason.BYPASS
    else:
        raise AssertionError("direct path should be rejected")

    b2 = GatedBroker()
    legitimate_path(b2)
    assert len(b2.fills) == 1
    print("POC2_OK: direct strategy->broker blocked; risk_engine path allowed")


if __name__ == "__main__":
    main()
