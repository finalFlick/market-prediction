"""POC 1: byte-identical metrics.json via canonical JSON + fixed seed."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any

import numpy as np

RNG = np.random.Generator(np.random.PCG64(42))


def run_backtest(
    data: np.ndarray,
    _strategy: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    window = int(config["window"])
    rets = np.diff(np.log(np.maximum(data, 1e-12)))
    signal = np.zeros(len(rets), dtype=np.float64)
    for i in range(window, len(rets)):
        past = rets[i - window : i]
        signal[i] = float(np.mean(past) > 0) * 2 - 1
    strat_rets = signal[window:] * rets[window:]
    eq = float(np.cumprod(1.0 + strat_rets)[-1])
    total_return = float(eq - 1.0)
    sharpe = float(np.sqrt(252) * np.mean(strat_rets) / (np.std(strat_rets) + 1e-12))
    mdd = _max_drawdown(strat_rets)
    return {
        "schema_version": "poc-1",
        "total_return": total_return,
        "sharpe": sharpe,
        "max_drawdown": mdd,
        "n_bars": int(len(strat_rets)),
    }


def _max_drawdown(returns: np.ndarray) -> float:
    wealth = np.cumprod(1.0 + returns)
    peak = np.maximum.accumulate(wealth)
    dd = (wealth - peak) / (peak + 1e-12)
    return float(np.min(dd))


def _to_canonical_obj(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _to_canonical_obj(obj[k]) for k in sorted(obj.keys())}
    if isinstance(obj, list):
        return [_to_canonical_obj(x) for x in obj]
    if obj is None or isinstance(obj, bool):
        return obj
    if isinstance(obj, str):
        return obj
    if isinstance(obj, int):
        return obj
    if isinstance(obj, float):
        if not np.isfinite(obj):
            raise ValueError("non-finite")
        d = Decimal(str(obj))
        return format(d, ".8f")
    raise TypeError(type(obj))


def metrics_to_bytes(metrics: dict[str, Any]) -> bytes:
    canonical = _to_canonical_obj(metrics)
    s = json.dumps(
        canonical,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return (s + "\n").encode("utf-8")


def main() -> None:
    data = RNG.lognormal(mean=0.0, sigma=0.01, size=500).astype(np.float64) * 100 + 50.0
    config = {"window": 20}
    m1 = run_backtest(data, "sign_mom", config)
    m2 = run_backtest(data, "sign_mom", config)
    b1 = metrics_to_bytes(m1)
    b2 = metrics_to_bytes(m2)
    h1 = hashlib.sha256(b1).hexdigest()
    h2 = hashlib.sha256(b2).hexdigest()
    assert h1 == h2, "determinism failed"
    print("POC1_OK")
    print(f"sha256(metrics.json bytes) = {h1}")


if __name__ == "__main__":
    main()
