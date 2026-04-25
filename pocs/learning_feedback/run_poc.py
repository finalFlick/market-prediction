"""POC 8: score a few simple signals; higher score should track injected edge when present."""

from __future__ import annotations

import numpy as np

RNG = np.random.Generator(np.random.PCG64(1))


def pnl_of_signal(fwd: np.ndarray, z: np.ndarray) -> float:
    pos = np.tanh(z)
    sret = pos * fwd
    return float(sret.sum())


def main() -> None:
    t = 500
    p = 100.0
    rets: list[float] = []
    for i in range(t - 1):
        r = float(RNG.normal(0, 0.01))
        rets.append(r)
        p = p * (1.0 + r)
    f = np.asarray(rets, dtype=np.float64)
    # 3 "signals" — one has tiny correlation with f (edge); others are noise
    c = 0.18
    s_mom = np.cumsum(f) - np.cumsum(f) * 0.0
    s_mom = c * f + RNG.normal(0, 0.5, size=t - 1)
    s_vol = f**2 + RNG.normal(0, 0.2, size=t - 1)
    s_sen = RNG.normal(0, 0.2, size=t - 1)
    scores = {
        "momentum": pnl_of_signal(f, s_mom),
        "volume_spike": pnl_of_signal(f, s_vol),
        "sentiment": pnl_of_signal(f, s_sen),
    }
    ranked = sorted(scores, key=scores.get, reverse=True)  # type: ignore[arg-type, return-value]
    # momentum should win because we added c*f
    if ranked[0] != "momentum":
        print("POC8_INFO: with this seed, ranking order:", ranked, scores)
    else:
        print("POC8_OK: best-ranked signal = momentum (injected match to fwd)")

    hit_mom = float(
        np.mean(
            (np.tanh(s_mom) * f) > 0.0
        )
    )
    _ = hit_mom
    print(
        f"POC8_done: pnl_mom={scores['momentum']:.4f} pnl_vol={scores['volume_spike']:.4f} pnl_sen={scores['sentiment']:.4f}"
    )


if __name__ == "__main__":
    main()
