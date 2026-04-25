"""Live broker registration is locked by default at MVP-0."""

from __future__ import annotations

import importlib

import pytest

from execution.brokers.binance import BinanceBroker, BinanceLive
from execution.brokers.coinbase import CoinbaseBroker, CoinbaseLive
from execution.brokers.paper import PaperBroker
from execution.brokers.registry import (
    LiveAdapterRegistrationForbidden,
    LiveBrokerRegistry,
)


@pytest.mark.security
def test_live_registration_forbidden_by_default() -> None:
    registry = LiveBrokerRegistry()

    with pytest.raises(LiveAdapterRegistrationForbidden) as excinfo:
        registry.register(BinanceBroker())
    assert excinfo.value.broker == "binance"
    assert excinfo.value.reason == "pre_live_gate_not_passed_or_flag_off"

    with pytest.raises(LiveAdapterRegistrationForbidden) as excinfo:
        registry.register(CoinbaseBroker())
    assert excinfo.value.broker == "coinbase"
    assert excinfo.value.reason == "pre_live_gate_not_passed_or_flag_off"


@pytest.mark.security
def test_paper_broker_allowed_while_live_locked() -> None:
    registry = LiveBrokerRegistry()
    paper = PaperBroker()
    registry.register(paper)

    assert registry.brokers[paper.name] is paper


@pytest.mark.security
def test_live_registration_allowed_when_unlocked_provider_true() -> None:
    registry = LiveBrokerRegistry(unlocked_provider=lambda: True)
    broker = BinanceBroker()

    registry.register(broker)

    assert registry.brokers[broker.name] is broker


@pytest.mark.security
def test_importing_live_modules_has_no_registration_side_effect() -> None:
    registry = LiveBrokerRegistry()
    importlib.import_module("execution.brokers.binance")
    importlib.import_module("execution.brokers.coinbase")

    assert registry.brokers == {}


@pytest.mark.security
def test_live_aliases_match_broker_classes() -> None:
    assert BinanceLive is BinanceBroker
    assert CoinbaseLive is CoinbaseBroker
