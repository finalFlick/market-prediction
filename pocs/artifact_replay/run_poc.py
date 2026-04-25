"""POC 3: run artifacts + replay_run reproduces same canonical metrics hash."""

from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

# Reuse deterministic core from sibling POC (duplicated minimal to keep standalone)
RNG = np.random.Generator(np.random.PCG64(7))


def _max_drawdown(returns: np.ndarray) -> float:
    wealth = np.cumprod(1.0 + returns)
    peak = np.maximum.accumulate(wealth)
    dd = (wealth - peak) / (peak + 1e-12)
    return float(np.min(dd))


def run_experiment(
    data: np.ndarray, config: dict[str, Any]
) -> dict[str, Any]:
    window = int(config["window"])
    rets = np.diff(np.log(np.maximum(data, 1e-12)))
    signal = (np.cumsum(rets) - np.cumsum(rets).mean()) * 0
    signal = np.sign(np.r_[0, rets][1:])  # simple
    signal = np.zeros(len(rets))
    for i in range(window, len(rets)):
        signal[i] = 1.0 if np.sum(rets[i - window : i]) > 0 else -1.0
    sr = signal[window:] * rets[window:]
    return {
        "schema_version": "poc-artifact-1",
        "total_return": float(np.prod(1.0 + sr) - 1.0),
        "sharpe": float(np.sqrt(252) * np.mean(sr) / (np.std(sr) + 1e-12)),
        "max_drawdown": _max_drawdown(sr),
    }


def canonical_hash(metrics: dict[str, Any]) -> str:
    from decimal import Decimal

    def norm(o: Any) -> Any:
        if isinstance(o, dict):
            return {k: norm(o[k]) for k in sorted(o.keys())}
        if isinstance(o, float):
            d = Decimal(str(o))
            return format(d, ".8f")
        return o

    s = json.dumps(
        norm(metrics), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ) + "\n"
    return hashlib.sha256(s.encode()).hexdigest()


def write_run(run_id: str, out: Path) -> None:
    data = RNG.lognormal(0, 0.01, 300).astype(np.float64) * 50 + 20.0
    config = {"window": 10, "run_id": run_id}
    rdir = out / run_id
    rdir.mkdir(parents=True, exist_ok=True)
    (rdir / "config.json").write_text(
        json.dumps(config, sort_keys=True, indent=2), encoding="utf-8"
    )
    (rdir / "data.npy").write_bytes(data.tobytes())
    meta = json.dumps(
        {"dtype": str(data.dtype), "shape": list(data.shape)}
    )
    (rdir / "data_meta.json").write_text(meta, encoding="utf-8")
    m = run_experiment(data, config)
    (rdir / "metrics.json").write_text(
        json.dumps(m, sort_keys=True, indent=2), encoding="utf-8"
    )


def load_and_replay(rdir: Path) -> str:
    config = json.loads((rdir / "config.json").read_text(encoding="utf-8"))
    meta = json.loads((rdir / "data_meta.json").read_text(encoding="utf-8"))
    raw = np.frombuffer(
        (rdir / "data.npy").read_bytes(), dtype=np.dtype(meta["dtype"])
    ).reshape(meta["shape"])
    metrics = run_experiment(raw, config)
    return canonical_hash(metrics)


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        write_run("run-001", p)
        h_disk = canonical_hash(
            json.loads((p / "run-001" / "metrics.json").read_text(encoding="utf-8"))
        )
        h_replay = load_and_replay(p / "run-001")
        assert h_disk == h_replay
    print("POC3_OK: replay metrics hash matches stored metrics hash")


if __name__ == "__main__":
    main()
