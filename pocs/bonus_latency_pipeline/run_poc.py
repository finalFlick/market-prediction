"""Bonus: micro timing + 1M-row candle scan (rough)."""

from __future__ import annotations

import time

import numpy as np
import pandas as pd

RNG = np.random.Generator(np.random.PCG64(3))


def main() -> None:
    t0 = time.perf_counter()
    for i in range(5_000):
        _ = float(i) * 0.0 + 1.0
    t1 = time.perf_counter()
    print(f"POC_bonus_latency: 5k no-op loop {1e6 * (t1 - t0) / 5000:.1f} us/iter (order of Python overhead)")

    n = 1_000_000
    t2 = time.perf_counter()
    o = RNG.random(n, dtype=np.float64) * 100.0
    h = o * 1.001
    l = o * 0.999
    c = o * 1.0001
    df = pd.DataFrame({"o": o, "h": h, "l": l, "c": c})
    t3 = time.perf_counter()
    _ = (df["c"] / df["c"].shift(1) - 1.0).fillna(0.0)
    t4 = time.perf_counter()
    print(
        f"POC_bonus_pipeline: {n} rows build+ret {t3 - t2:.3f}s read ret {t4 - t3:.3f}s"
    )
    if t3 - t2 < 10.0:
        print("POC_bonus_OK: 1M candles in-memory in single-digit seconds (typical on dev CPU)")


if __name__ == "__main__":
    main()
