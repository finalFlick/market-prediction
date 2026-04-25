"""FastAPI dependency providers.

A single connection per request. Connections are short-lived; the engine is
the long-running writer and uses its own connection.
"""

from __future__ import annotations

from collections.abc import Generator

from data.repositories import (
    BacktestsRepo,
    SignalsRepo,
    StrategiesRepo,
    TradesRepo,
)


def trades_repo() -> Generator[TradesRepo, None, None]:
    repo = TradesRepo()
    try:
        yield repo
    finally:
        repo.close()


def strategies_repo() -> Generator[StrategiesRepo, None, None]:
    repo = StrategiesRepo()
    try:
        yield repo
    finally:
        repo.close()


def signals_repo() -> Generator[SignalsRepo, None, None]:
    repo = SignalsRepo()
    try:
        yield repo
    finally:
        repo.close()


def backtests_repo() -> Generator[BacktestsRepo, None, None]:
    repo = BacktestsRepo()
    try:
        yield repo
    finally:
        repo.close()
