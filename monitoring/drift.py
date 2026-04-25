"""Live-vs-backtest drift detection.

Compares realized PnL distribution to the backtest distribution and emits an
alert when the standardized difference exceeds a configurable threshold.
Implementation intentionally stubbed — the interface is what matters.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from monitoring.logger import get_logger

log = get_logger(__name__)


@dataclass(frozen=True)
class DriftReport:
    metric: str
    expected_mean: float
    expected_std: float
    realized_mean: float
    z_score: float
    threshold: float

    @property
    def breached(self) -> bool:
        return abs(self.z_score) > self.threshold


def detect_drift(
    realized: np.ndarray,
    expected_mean: float,
    expected_std: float,
    *,
    metric: str = "pnl",
    threshold: float = 3.0,
) -> DriftReport:
    """Return a DriftReport comparing `realized` to (expected_mean, expected_std)."""
    if expected_std <= 0:
        raise ValueError("expected_std must be positive")
    if realized.size == 0:
        raise ValueError("realized must be non-empty")

    realized_mean = float(np.mean(realized))
    n = realized.size
    z = (realized_mean - expected_mean) / (expected_std / np.sqrt(n))
    report = DriftReport(
        metric=metric,
        expected_mean=expected_mean,
        expected_std=expected_std,
        realized_mean=realized_mean,
        z_score=float(z),
        threshold=threshold,
    )
    if report.breached:
        log.warning("drift.breach", **report.__dict__)
    return report
