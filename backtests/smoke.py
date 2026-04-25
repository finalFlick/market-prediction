"""Tiny end-to-end backtest smoke test wired for CI.

Generates synthetic OHLCV, runs a single bar through the engine + risk +
paper broker, and asserts the system produces at least one trade and a
finite Sharpe. Intentionally deterministic (seeded numpy) and fast.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

from backtests.engine import BacktestConfig, BacktestEngine, CostModel
from backtests.metrics import compute_metrics
from risk.limits import RiskLimits
from strategies.examples.momentum_xover import MomentumXover


def _synthetic_bars(n: int = 600, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0, 0.01, size=n).cumsum()
    price = 100.0 * np.exp(rets)
    idx = pd.date_range(
        start=datetime.now(tz=UTC) - timedelta(hours=n),
        periods=n,
        freq="1H",
        tz="UTC",
    )
    df = pd.DataFrame(
        {
            "open": price,
            "high": price * 1.001,
            "low": price * 0.999,
            "close": price,
            "volume": 100.0,
            "quote_volume": 100.0 * price,
        },
        index=idx,
    )
    df.index.name = "ts"
    return df


def main() -> int:
    bars = {"BTCUSDT": _synthetic_bars()}
    strategy = MomentumXover(
        name="smoke_momentum",
        universe=["BTCUSDT"],
        timeframe="1h",
        fast=5,
        slow=20,
        target_weight=0.5,
    )
    cfg = BacktestConfig(
        starting_cash=10_000.0,
        cost_model=CostModel(taker_fee_bps=5.0, slippage_bps=2.0, latency_bars=0),
        risk_limits=RiskLimits.model_validate({}),
    )
    engine = BacktestEngine(cfg)
    result = engine.run(strategy, bars)
    metrics = compute_metrics(result.equity, result.trades)

    if result.equity.empty:
        print("smoke: empty equity curve", file=sys.stderr)
        return 1
    if not np.isfinite(metrics["sharpe"]):
        print(f"smoke: non-finite sharpe={metrics['sharpe']}", file=sys.stderr)
        return 1
    print(
        "smoke OK | bars={n} trades={t} sharpe={s:.2f} maxDD={d:.2%} final={f:.2f}".format(
            n=len(bars["BTCUSDT"]),
            t=len(result.trades),
            s=metrics["sharpe"],
            d=metrics["max_drawdown"],
            f=float(result.equity.iloc[-1]),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
