"""Inv-3 (file-level): two runs of the same BacktestSpec produce byte-identical metrics.json.

This extends the in-memory test in test_backtest_determinism.py to verify that
write_canonical_json + compute_metrics round-trips through disk produce
identical byte streams (sha256 and length).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from backtests.engine import BacktestConfig, BacktestEngine, CostModel
from backtests.metrics import compute_metrics
from backtests.smoke import _synthetic_bars
from monitoring.canonical_json import write_canonical_json
from risk.limits import RiskLimits
from strategies.examples.momentum_xover import MomentumXover


def _run_and_write(results_dir: Path, run_name: str) -> Path:
    bars = {"BTCUSDT": _synthetic_bars(n=400, seed=7)}
    strategy = MomentumXover(
        name="det_file_momo",
        universe=["BTCUSDT"],
        timeframe="1h",
        fast=5,
        slow=20,
        target_weight=0.4,
    )
    cfg = BacktestConfig(
        starting_cash=10_000.0,
        cost_model=CostModel(taker_fee_bps=5.0, slippage_bps=2.0, latency_bars=0),
        risk_limits=RiskLimits.model_validate({}),
        seed=42,
    )
    result = BacktestEngine(cfg).run(strategy, bars)
    metrics = compute_metrics(result.equity, result.trades)

    run_dir = results_dir / run_name
    run_dir.mkdir()
    out = run_dir / "metrics.json"
    write_canonical_json(out, metrics)
    return out


@pytest.mark.det
def test_metrics_json_byte_identical_across_two_runs(tmp_path: Path) -> None:
    run_a = _run_and_write(tmp_path, "run_a")
    run_b = _run_and_write(tmp_path, "run_b")

    bytes_a = run_a.read_bytes()
    bytes_b = run_b.read_bytes()

    assert len(bytes_a) == len(bytes_b), (
        f"metrics.json length differs: {len(bytes_a)} vs {len(bytes_b)}"
    )
    assert hashlib.sha256(bytes_a).hexdigest() == hashlib.sha256(bytes_b).hexdigest(), (
        f"metrics.json sha256 differs.\nrun_a: {bytes_a!r}\nrun_b: {bytes_b!r}"
    )


@pytest.mark.det
def test_metrics_json_is_valid_json(tmp_path: Path) -> None:
    out = _run_and_write(tmp_path, "validate")
    parsed = json.loads(out.read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)
    assert "sharpe" in parsed
    assert "max_drawdown" in parsed
