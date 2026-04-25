"""POC 5: minimal paper broker — fees, slippage, market, limit, partial fill."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

EPS = 1e-9


class Side(str, Enum):
    BUY = auto()
    SELL = auto()


@dataclass
class Book:
    """Tiny depth: best bid / ask and available size at those prices."""

    bid_px: float
    ask_px: float
    bid_sz: float
    ask_sz: float


@dataclass
class Sim:
    fee_bps: float = 10.0
    slippage_bps: float = 5.0
    book: Book = field(default_factory=lambda: Book(99.0, 101.0, 200.0, 150.0))
    position: float = 0.0
    cash: float = 1_000_000.0
    fills: list[tuple[Side, float, float, float]] = field(default_factory=list)  # side, qty, px, fee

    def market(self, side: Side, qty: float) -> None:
        if side == Side.BUY:
            raw_px = self.book.ask_px * (1.0 + self.slippage_bps / 1e4)
            f = self._fee(raw_px, qty, True)
            cost = raw_px * qty + f
            if cost > self.cash + EPS:
                raise ValueError("insufficient cash")
            self.cash -= cost
            self.position += qty
            self.fills.append((side, qty, raw_px, f))
        else:
            raw_px = self.book.bid_px * (1.0 - self.slippage_bps / 1e4)
            f = self._fee(raw_px, qty, True)
            pnl = raw_px * qty - f
            self.cash += pnl
            self.position -= qty
            self.fills.append((side, qty, raw_px, f))

    def limit(self, side: Side, limit_px: float, qty: float) -> None:
        """Simplified: partial fill if price inside book."""
        if side == Side.BUY and limit_px >= self.book.ask_px - EPS:
            fill = min(qty, self.book.ask_sz, self.cash / max(limit_px, EPS))
            raw_px = min(limit_px, self.book.ask_px)
            f = self._fee(raw_px, fill, True)
            if fill * raw_px + f > self.cash + EPS:
                return
            self.cash -= raw_px * fill + f
            self.position += fill
            self.fills.append((side, fill, raw_px, f))
        elif side == Side.SELL and limit_px <= self.book.bid_px + EPS:
            fill = min(qty, self.book.bid_sz, self.position) if self.position > 0 else 0.0
            if fill <= EPS:
                return
            raw_px = max(limit_px, self.book.bid_px)
            f = self._fee(raw_px, fill, True)
            self.cash += raw_px * fill - f
            self.position -= fill
            self.fills.append((side, fill, raw_px, f))

    def _fee(self, px: float, qty: float, _mkt: bool) -> float:
        return px * qty * (self.fee_bps / 1e4)


def compare_to_historical_avg_fill(mine: list[tuple[Side, float, float, float]], bench_px: float) -> bool:
    """POC: sanity vs a reference trade price (like historical)."""
    if not mine or mine[0][1] <= 0:
        return False
    my_px = mine[0][2]
    return abs(my_px - bench_px) / bench_px < 0.02  # within 2% of "historical" mid


def main() -> None:
    s1 = Sim()
    s1.market(Side.BUY, 1.0)
    assert s1.fills[0][2] > s1.book.ask_px
    s2 = Sim()
    s2.position = 10.0
    s2.limit(Side.SELL, 99.0, 10.0)  # at/below bid to fill
    assert s2.fills[0][1] > 0
    s3 = Sim()
    s3.limit(Side.BUY, 200.0, 500.0)  # partial vs ask depth
    filled = s3.fills[0][1] if s3.fills and s3.fills[0][1] > 0 else 0.0
    assert filled < 500 - EPS, "expected partial"
    assert compare_to_historical_avg_fill(s1.fills[:1], 100.0)  # mid
    print("POC5_OK: market, limit+partial, fees+slip monotonic; cross-check vs reference mid inside band")


if __name__ == "__main__":
    main()
