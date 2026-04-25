"""Smoke tests: every top-level module imports without errors."""

from __future__ import annotations

import importlib

import pytest

_TOP_LEVEL = [
    "data",
    "data.db",
    "data.store",
    "data.types",
    "data.ingest",
    "data.ingest.base",
    "data.ingest.binance",
    "data.ingest.coinbase",
    "data.repositories",
    "data.repositories.signals_repo",
    "data.repositories.strategies_repo",
    "data.repositories.trades_repo",
    "data.repositories.backtests_repo",
    "research",
    "research.labels",
    "research.cv",
    "research.features",
    "research.features.price",
    "research.features.volume",
    "research.features.momentum",
    "research.features.validation",
    "research.models",
    "research.models.base",
    "research.models.registry",
    "research.llm",
    "research.llm.client",
    "research.llm.prompts",
    "strategies",
    "strategies.base",
    "strategies.composer",
    "strategies.examples.momentum_xover",
    "risk",
    "risk.engine",
    "risk.limits",
    "risk.sizing",
    "risk.types",
    "backtests",
    "backtests.engine",
    "backtests.metrics",
    "backtests.manifest",
    "backtests.smoke",
    "execution",
    "execution.brokers.base",
    "execution.brokers.paper",
    "execution.brokers.binance",
    "execution.brokers.coinbase",
    "monitoring",
    "monitoring.logger",
    "monitoring.metrics",
    "monitoring.drift",
    "backend",
    "backend.api",
    "backend.api.app",
    "backend.api.deps",
    "backend.api.routers.trades",
    "backend.api.routers.strategies",
    "backend.api.routers.signals",
    "backend.api.routers.backtests",
    "backend.api.routers.system",
]


@pytest.mark.parametrize("module", _TOP_LEVEL)
def test_module_imports(module: str) -> None:
    importlib.import_module(module)
