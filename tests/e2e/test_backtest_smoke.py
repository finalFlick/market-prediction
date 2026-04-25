"""Run the backtest smoke entrypoint as a sub-test of the system."""

from __future__ import annotations

import pytest

from backtests.smoke import main


@pytest.mark.e2e
def test_backtest_smoke_returns_zero() -> None:
    assert main() == 0
