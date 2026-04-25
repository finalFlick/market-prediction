"""Performance metrics for a backtest result."""

from __future__ import annotations

import numpy as np
import pandas as pd

_MIN_INDEX_LEN = 2


def compute_metrics(equity: pd.Series, trades: pd.DataFrame) -> dict[str, float]:
    """Return Sharpe, Sortino, max drawdown, CAGR, hit rate, turnover."""
    if equity.empty:
        return {}

    rets = equity.pct_change().dropna()
    if rets.empty:
        return {"final_equity": float(equity.iloc[-1])}

    bars_per_year = _bars_per_year(equity.index)
    mean = float(rets.mean())
    std = float(rets.std()) or 1e-12
    downside = float(rets.clip(upper=0).std()) or 1e-12
    sharpe = mean / std * np.sqrt(bars_per_year)
    sortino = mean / downside * np.sqrt(bars_per_year)

    running_max = equity.cummax()
    drawdown = (equity - running_max) / running_max
    max_dd = float(drawdown.min())

    duration_years = (equity.index[-1] - equity.index[0]).total_seconds() / (365.25 * 24 * 3600)
    if duration_years > 0:
        cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / duration_years) - 1
    else:
        cagr = 0.0

    hit_rate = 0.0
    turnover = 0.0
    if not trades.empty:
        notional = (trades["qty"] * trades["price"]).abs().sum()
        turnover = float(notional / equity.iloc[0]) if equity.iloc[0] > 0 else 0.0

        # Approximate per-trade pnl by pairing buys/sells per symbol FIFO.
        pnls: list[float] = []
        for _, group in trades.groupby("symbol"):
            qty = 0.0
            avg = 0.0
            for _, row in group.sort_values("ts").iterrows():
                signed = row["qty"] if row["side"] == "buy" else -row["qty"]
                if qty == 0 or np.sign(qty) == np.sign(signed):
                    if (qty + signed) != 0:
                        avg = (qty * avg + signed * row["price"]) / (qty + signed)
                    qty += signed
                else:
                    closed = min(abs(signed), abs(qty)) * np.sign(qty)
                    pnls.append((row["price"] - avg) * closed)
                    qty += signed
                    if qty == 0:
                        avg = 0.0
        if pnls:
            hit_rate = float(np.mean([1.0 if p > 0 else 0.0 for p in pnls]))

    return {
        "final_equity": float(equity.iloc[-1]),
        "sharpe": float(sharpe),
        "sortino": float(sortino),
        "max_drawdown": max_dd,
        "cagr": float(cagr),
        "hit_rate": hit_rate,
        "turnover": turnover,
    }


def _bars_per_year(index: pd.DatetimeIndex) -> float:
    if len(index) < _MIN_INDEX_LEN:
        return 1.0
    delta = (index[-1] - index[0]).total_seconds()
    if delta <= 0:
        return 1.0
    return float((len(index) - 1) * (365.25 * 24 * 3600) / delta)
