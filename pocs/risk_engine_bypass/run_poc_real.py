"""POC 2b: use project RiskEngine — orders only exist after check_and_size."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from risk.engine import RiskEngine
    from risk.limits import RiskLimits
    from risk.types import OrderSide, Portfolio, TargetPosition
except ModuleNotFoundError as err:
    print(
        f"POC2b_SKIP: project deps not installed (need structlog, etc.): {err} "
        "Run: pip install -e .  then re-run this script."
    )
    raise SystemExit(0) from err

# Intention: no Order objects exist for execution except those returned by RiskEngine.


def main() -> None:
    lim = RiskLimits(
        max_gross_exposure=1.0,
        max_net_exposure=1.0,
        max_per_symbol_weight=0.5,
        max_leverage=1.0,
        max_daily_loss_pct=0.99,
        max_drawdown_pct=0.99,
        min_order_notional=0.0,
        target_annual_vol=0.15,
        kill_switch=False,
    )
    engine = RiskEngine(lim)
    ts = datetime.now(tz=timezone.utc)
    portfolio = Portfolio(
        ts=ts,
        cash=100_000.0,
        positions={},
        realized_pnl_today=0.0,
        high_water_mark=100_000.0,
    )
    marks = {"BTC": 50_000.0}
    vol = {"BTC": 0.4}
    targets = [TargetPosition(symbol="BTC", weight=0.1)]
    orders = engine.check_and_size(targets, portfolio, marks, vol)
    assert all(o.side == OrderSide.BUY for o in orders)
    assert len(orders) == 1
    print("POC2b_OK: RiskEngine emitted orders; no other factory for live orders in this path")


if __name__ == "__main__":
    main()
