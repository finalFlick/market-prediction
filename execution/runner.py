"""Live runner: tick → strategy → risk → broker → monitoring.

Wires the full pipeline at runtime. Defaults to the paper broker for safety;
explicit `--broker binance|coinbase` is required to touch a live exchange.
"""

from __future__ import annotations

import asyncio
import importlib
from datetime import UTC, datetime

import click

from execution.brokers.base import Broker
from execution.brokers.binance import BinanceLive
from execution.brokers.coinbase import CoinbaseLive
from execution.brokers.paper import PaperBroker
from execution.brokers.registry import LiveAdapterRegistrationForbidden, LiveBrokerRegistry
from monitoring.logger import get_logger
from risk.engine import RiskEngine
from risk.errors import RiskCheckRejected
from risk.limits import RiskLimits
from risk.types import Portfolio, TargetPosition
from strategies.base import Strategy

log = get_logger(__name__)

_BROKERS: dict[str, type[Broker]] = {
    "paper": PaperBroker,
    "binance": BinanceLive,
    "coinbase": CoinbaseLive,
}


def _import_strategy(dotted: str) -> type[Strategy]:
    module_path, _, attr = dotted.rpartition(".")
    if not module_path:
        raise click.BadParameter(f"strategy must be 'module.ClassName', got '{dotted}'")
    mod = importlib.import_module(module_path)
    obj = getattr(mod, attr, None)
    if obj is None:
        candidates = [
            v
            for v in vars(mod).values()
            if isinstance(v, type) and issubclass(v, Strategy) and v is not Strategy
        ]
        if not candidates:
            raise click.BadParameter(f"no Strategy subclass in {module_path}")
        return candidates[0]
    if not (isinstance(obj, type) and issubclass(obj, Strategy)):
        raise click.BadParameter(f"{dotted} is not a Strategy subclass")
    return obj


async def _run(broker: Broker, strategy: Strategy, risk: RiskEngine) -> None:
    """One iteration of the live loop. Replace with an event-driven loop later."""
    portfolio = Portfolio(ts=datetime.now(tz=UTC), cash=0.0)
    log.info("runner.start", broker=broker.name, strategy=strategy.name, universe=strategy.universe)

    # The full implementation subscribes to data.stream, builds MarketState
    # incrementally, calls strategy.target_positions on each bar close, runs
    # risk.check_and_size, and routes orders through `broker.place_order`.
    # Surface the entrypoints clearly so the next agent can implement them
    # without reshaping the module.
    targets: list[TargetPosition] = []
    try:
        orders = risk.check_and_size(targets, portfolio, marks={}, realized_vol={})
    except RiskCheckRejected as exc:
        log.warning("runner.reject", rule=exc.rule, message=exc.message)
        orders = []

    for order in orders:
        await broker.place_order(order)


@click.command()
@click.option("--broker", "broker_name", type=click.Choice(list(_BROKERS)), default="paper")
@click.option("--strategy", "strategy_dotted", required=True)
def main(broker_name: str, strategy_dotted: str) -> None:
    registry = LiveBrokerRegistry()
    registry.register(PaperBroker())
    if broker_name == "paper":
        broker = registry.brokers["paper"]
    else:
        broker_cls = _BROKERS[broker_name]
        try:
            broker = broker_cls()
            registry.register(broker)
        except LiveAdapterRegistrationForbidden as exc:
            raise click.ClickException(f"broker '{exc.broker}' is locked: {exc.reason}") from exc

    strategy_cls = _import_strategy(strategy_dotted)
    strategy = strategy_cls()
    risk = RiskEngine(RiskLimits.model_validate({}))
    asyncio.run(_run(broker, strategy, risk))


if __name__ == "__main__":
    main()
