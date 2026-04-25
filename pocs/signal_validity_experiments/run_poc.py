"""POC+ : 4 quants' first experiments on a synthetic 2D return panel (rough)."""

from __future__ import annotations

import numpy as np

RNG = np.random.Generator(np.random.PCG64(99))


def _panel(assets: int, steps: int) -> np.ndarray:
    """(steps, assets) return matrix, tiny cross-sectional momentum factor."""
    f = 0.02
    fmat = f * (RNG.normal(0, 0.1, (steps, 1)) @ RNG.normal(0, 0.1, (1, assets)))
    idio = RNG.normal(0, 0.15, (steps, assets)) * 0.01
    r = 0.05 * fmat + idio
    return r


def momentum_cs(r: np.ndarray, w: int = 20) -> float:
    """Long top quintile, short bottom; step through time (POC, not a real backtest)."""
    t, a = r.shape
    p = 0.0
    for t0 in range(w, t, 2):
        past = r[t0 - w : t0, :]
        s = past.sum(0)
        o = s.argsort()
        q = max(1, a // 5)
        long, short_ = o[-q:], o[:q]  # best = high prior sum, worst = low
        sret = r[t0, long].mean() - r[t0, short_].mean()
        p += float(sret)
    return p


def mean_reversion_rsi_simple(r1d: np.ndarray, g: int = 5) -> float:
    c = 0.0
    d = r1d
    for i in range(g, len(d) - 1):
        wnd = d[i - g : i]
        u = wnd[wnd > 0].sum()
        dnw = -wnd[wnd < 0].sum() + 1e-9
        rs = u / dnw
        rsi = 100.0 - 100.0 / (1.0 + rs)
        c += d[i + 1] * (0.0 if 30.0 < rsi < 70.0 else 0.1)
    return float(c)


def hurst_proxy(s: np.ndarray) -> float:
    """Not a real Hurst; variance ratio stand-in in [0,1] for POC only."""
    if len(s) < 4:
        return 0.5
    m = 2
    b = s[::m]
    v = (np.std(b) + 1e-9) / (np.std(s) + 1e-9)
    h = 0.5 + 0.1 * float(np.tanh((v - 1.0) * 2.0))
    return max(0.0, min(1.0, h))


def main() -> None:
    r2 = _panel(15, 400)
    mom = momentum_cs(r2, w=25)
    r1d = r2.mean(axis=1)
    mrev = mean_reversion_rsi_simple(r1d)
    h = hurst_proxy((r1d * 100.0).cumsum())
    print("POC_signal_studies: synthetic data only - do not infer live edge")
    print(
        f"  momentum_xsection_cum~{mom:.4f} mean_reversion~{mrev:.4f} "
        f"hurst_proxy~{h:.2f}"
    )
    if mom > 0.0:
        print("POC+_OK: momentum proxy positive on this synthetic (weak factor in mix)")
    else:
        print("POC+_INFO: momentum sign depends on this seed")


if __name__ == "__main__":
    main()
