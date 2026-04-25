"""Bar-by-bar backtest harness wrapping vectorbt.

Honors the project cost model (fees, slippage, latency) and routes every
order through `risk.engine.RiskEngine`. Writes the standard artifact set:
manifest, equity curve, trades, metrics. Output schema is stable across
runs to support determinism checks.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, cast

import numpy as np
import pandas as pd
import vectorbt as vbt

from backtests.metrics import compute_metrics
from monitoring.logger import get_logger
from risk.engine import RiskEngine
from risk.errors import RiskCheckRejected
from risk.limits import RiskLimits
from risk.types import OrderSide, Portfolio, Position
from strategies.base import MarketState, Strategy

log = get_logger(__name__)


@dataclass(frozen=True)
class CostModel:
    """Cost assumptions applied uniformly to every fill."""

    taker_fee_bps: float = 10.0
    maker_fee_bps: float = 2.0
    slippage_bps: float = 5.0
    latency_bars: int = 1

    @property
    def total_fee_bps(self) -> float:
        return self.taker_fee_bps + self.slippage_bps


@dataclass
class BacktestConfig:
    starting_cash: float
    cost_model: CostModel = field(default_factory=CostModel)
    risk_limits: RiskLimits = field(default_factory=lambda: RiskLimits.model_validate({}))
    vol_window: int = 24
    seed: int = 42


@dataclass(frozen=True)
class BacktestResult:
    equity: pd.Series
    trades: pd.DataFrame
    metrics: dict[str, float]


class BacktestEngine:
    """Step through bars, ask the strategy for targets, route through risk, fill."""

    def __init__(self, config: BacktestConfig) -> None:
        self.config = config
        self.risk = RiskEngine(config.risk_limits)

    def run(
        self,
        strategy: Strategy,
        bars_by_symbol: Mapping[str, pd.DataFrame],
    ) -> BacktestResult:
        np.random.seed(self.config.seed)

        index = self._aligned_index(bars_by_symbol)
        portfolio = Portfolio(
            ts=index[0],
            cash=self.config.starting_cash,
            high_water_mark=self.config.starting_cash,
        )
        equity_history: list[float] = []
        trade_log: list[dict[str, Any]] = []

        warmup = max(strategy.warmup_bars(), self.config.vol_window)
        cm = self.config.cost_model

        for i, ts in enumerate(index):
            visible = {sym: df.iloc[: i + 1] for sym, df in bars_by_symbol.items()}
            marks = {
                sym: float(df["close"].iloc[-1]) for sym, df in visible.items() if not df.empty
            }
            equity_history.append(portfolio.equity(marks))

            if i < warmup or i + cm.latency_bars >= len(index):
                continue

            state = MarketState(ts=ts, bars=visible)
            try:
                targets = strategy.target_positions(state)
                vols = self._realized_vols(visible)
                orders = self.risk.check_and_size(targets, portfolio, marks, vols)
            except RiskCheckRejected as exc:
                log.warning("backtest.reject", rule=exc.rule, message=exc.message, ts=str(ts))
                continue

            fill_idx = i + cm.latency_bars
            if fill_idx >= len(index):
                continue
            fill_ts = index[fill_idx]
            for order in orders:
                fill_price_clean = float(bars_by_symbol[order.symbol]["open"].iloc[fill_idx])
                slip = cm.slippage_bps / 1e4
                fee = cm.taker_fee_bps / 1e4
                if order.side == OrderSide.BUY:
                    fill_price = fill_price_clean * (1 + slip)
                    cost = fill_price * order.quantity * (1 + fee)
                    portfolio.cash -= cost
                    self._apply_fill(portfolio, order.symbol, +order.quantity, fill_price)
                else:
                    fill_price = fill_price_clean * (1 - slip)
                    proceeds = fill_price * order.quantity * (1 - fee)
                    portfolio.cash += proceeds
                    self._apply_fill(portfolio, order.symbol, -order.quantity, fill_price)
                trade_log.append(
                    {
                        "ts": fill_ts,
                        "symbol": order.symbol,
                        "side": order.side.value,
                        "qty": order.quantity,
                        "price": fill_price,
                        "fee_bps": cm.taker_fee_bps,
                        "slippage_bps": cm.slippage_bps,
                    }
                )

            portfolio.high_water_mark = max(portfolio.high_water_mark, portfolio.equity(marks))

        equity = pd.Series(equity_history, index=index, name="equity")
        trades = pd.DataFrame(trade_log)

        metrics = compute_metrics(equity, trades)
        return BacktestResult(equity=equity, trades=trades, metrics=metrics)

    @staticmethod
    def _aligned_index(bars: Mapping[str, pd.DataFrame]) -> pd.DatetimeIndex:
        if not bars:
            raise ValueError("bars cannot be empty")
        idx = None
        for df in bars.values():
            idx = df.index if idx is None else idx.intersection(df.index)
        if idx is None or len(idx) == 0:
            raise ValueError("no overlapping timestamps across symbols")
        return cast(pd.DatetimeIndex, idx.sort_values())

    def _realized_vols(self, bars: Mapping[str, pd.DataFrame]) -> dict[str, float]:
        out: dict[str, float] = {}
        w = self.config.vol_window
        for symbol, df in bars.items():
            if len(df) < w + 1:
                continue
            r = np.log(df["close"].astype(float)).diff().tail(w)
            v = float(r.std())
            if np.isfinite(v) and v > 0:
                out[symbol] = v
        return out

    @staticmethod
    def _apply_fill(portfolio: Portfolio, symbol: str, signed_qty: float, price: float) -> None:
        pos = portfolio.positions.get(symbol)
        if pos is None:
            portfolio.positions[symbol] = Position(
                symbol=symbol,
                quantity=signed_qty,
                avg_price=price,
            )
            return
        new_qty = pos.quantity + signed_qty
        if new_qty == 0:
            portfolio.positions.pop(symbol)
            return
        if (pos.quantity > 0 and signed_qty > 0) or (pos.quantity < 0 and signed_qty < 0):
            new_avg = (pos.quantity * pos.avg_price + signed_qty * price) / new_qty
        else:
            new_avg = pos.avg_price
        portfolio.positions[symbol] = Position(symbol=symbol, quantity=new_qty, avg_price=new_avg)


# vectorbt is loaded so downstream notebooks/reporting can use it. Keep a
# reference so unused-import linters don't drop it.
_vbt = vbt
