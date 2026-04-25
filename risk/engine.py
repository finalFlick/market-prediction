"""The single, non-bypassable risk engine.

Every order — backtest, paper, or live — is produced by
`RiskEngine.check_and_size`. Strategies emit *target weights*; the engine
converts them to orders, applying sizing and rejecting any change that
violates a limit.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Literal, NoReturn

from monitoring.logger import get_logger
from monitoring.metrics import counter, gauge
from risk.audit import RiskAudit, RiskDecision
from risk.errors import RiskCheckRejected
from risk.limits import RiskLimits
from risk.sizing import clip_quantity_to_min_notional, vol_targeted_quantity
from risk.types import Order, OrderSide, Portfolio, TargetPosition

log = get_logger(__name__)


class RiskEngine:
    """Convert target weights into safe orders. Reject anything dangerous."""

    def __init__(
        self,
        limits: RiskLimits,
        *,
        audit: RiskAudit | None = None,
        run_id: str | None = None,
        client_id: str | None = None,
    ) -> None:
        self.limits = limits
        self._audit = audit
        self._run_id = run_id
        self._client_id = client_id

    def check_and_size(
        self,
        targets: Iterable[TargetPosition],
        portfolio: Portfolio,
        marks: dict[str, float],
        realized_vol: dict[str, float],
    ) -> list[Order]:
        """Return the list of orders that, if filled, move toward targets.

        Raises `RiskCheckRejected` for portfolio-level violations (kill-switch,
        daily loss, drawdown). Skips per-order violations with a logged warning
        and `metrics.counter('risk.reject', rule=...)`.
        """
        self._check_global(portfolio, marks)

        equity = portfolio.equity(marks)
        if equity <= 0:
            self._reject("equity_non_positive", f"equity={equity}", equity=equity)

        gauge("equity", equity)
        gauge("gross_exposure", portfolio.gross_exposure(marks))
        gauge("net_exposure", portfolio.net_exposure(marks))

        proposed: list[Order] = []
        target_qtys: dict[str, float] = {}
        for t in targets:
            self._check_per_symbol_weight(t.weight)
            mark = marks.get(t.symbol)
            vol = realized_vol.get(t.symbol)
            if mark is None or vol is None:
                log.warning("risk.skip", reason="missing_market_data", symbol=t.symbol)
                counter("risk.reject", rule="missing_market_data")
                self._emit(
                    "skip",
                    "missing_market_data",
                    f"missing mark or vol for {t.symbol}",
                    symbol=t.symbol,
                )
                continue
            qty = vol_targeted_quantity(
                target_weight=t.weight,
                equity=equity,
                price=mark,
                realized_vol=vol,
                target_annual_vol=self.limits.target_annual_vol,
            )
            qty = clip_quantity_to_min_notional(qty, mark, self.limits.min_order_notional)
            target_qtys[t.symbol] = qty

        # Diff against current positions to produce delta orders.
        for symbol, target_qty in target_qtys.items():
            current_position = portfolio.positions.get(symbol)
            current_qty = current_position.quantity if current_position is not None else 0.0
            delta = target_qty - current_qty
            if delta == 0.0:
                continue
            order = Order(
                symbol=symbol,
                side=OrderSide.BUY if delta > 0 else OrderSide.SELL,
                quantity=abs(delta),
            )
            proposed.append(order)

        # Final post-check: simulate the new portfolio and verify aggregate caps.
        self._check_aggregate(proposed, portfolio, marks, equity)
        counter("risk.orders_emitted", value=len(proposed))
        self._emit(
            "accept",
            "check_and_size",
            "orders approved",
            n_orders=len(proposed),
        )
        return proposed

    def _emit(
        self,
        outcome: Literal["accept", "reject", "skip"],
        rule: str,
        message: str = "",
        **details: object,
    ) -> None:
        if self._audit is None:
            return
        self._audit.emit(
            RiskDecision.new(
                run_id=self._run_id,
                client_id=self._client_id,
                rule=rule,
                outcome=outcome,
                message=message,
                **{k: v for k, v in details.items()},
            )
        )

    def _reject(self, rule: str, message: str, **details: object) -> NoReturn:
        self._emit("reject", rule, message, **details)
        raise RiskCheckRejected(rule, message)

    def _check_global(self, portfolio: Portfolio, marks: dict[str, float]) -> None:
        if self.limits.kill_switch:
            self._reject("kill_switch", "kill switch is engaged")

        equity = portfolio.equity(marks)
        if portfolio.realized_pnl_today < -self.limits.max_daily_loss_pct * equity:
            self._reject(
                "max_daily_loss",
                f"realized={portfolio.realized_pnl_today:.2f} > limit",
                equity=equity,
            )

        if portfolio.high_water_mark > 0:
            dd = (portfolio.high_water_mark - equity) / portfolio.high_water_mark
            if dd > self.limits.max_drawdown_pct:
                self._reject("max_drawdown", f"drawdown={dd:.2%}", drawdown=dd, equity=equity)

    def _check_per_symbol_weight(self, weight: float) -> None:
        if abs(weight) > self.limits.max_per_symbol_weight:
            self._reject(
                "max_per_symbol_weight",
                f"|weight|={abs(weight):.3f} > {self.limits.max_per_symbol_weight}",
                abs_weight=abs(weight),
            )

    def _check_aggregate(
        self,
        orders: list[Order],
        portfolio: Portfolio,
        marks: dict[str, float],
        equity: float,
    ) -> None:
        new_positions = {s: p.quantity for s, p in portfolio.positions.items()}
        for o in orders:
            sign = 1.0 if o.side == OrderSide.BUY else -1.0
            new_positions[o.symbol] = new_positions.get(o.symbol, 0.0) + sign * o.quantity

        gross = sum(abs(q) * marks.get(s, 0.0) for s, q in new_positions.items())
        net = sum(q * marks.get(s, 0.0) for s, q in new_positions.items())

        if gross > self.limits.max_gross_exposure * equity:
            self._reject(
                "max_gross_exposure",
                f"gross={gross:.2f} > {self.limits.max_gross_exposure * equity:.2f}",
                gross=gross,
            )
        if abs(net) > self.limits.max_net_exposure * equity:
            self._reject(
                "max_net_exposure",
                f"|net|={abs(net):.2f} > {self.limits.max_net_exposure * equity:.2f}",
                net=net,
            )
        leverage = gross / equity if equity > 0 else float("inf")
        if leverage > self.limits.max_leverage:
            self._reject(
                "max_leverage",
                f"leverage={leverage:.2f} > {self.limits.max_leverage}",
                leverage=leverage,
            )
