"""Typed summaries for learning — **out-of-sample metrics only**."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RunSummary(BaseModel, frozen=True):
    """Falsification metrics must come from OOS / purged-embargo outcomes only."""

    run_id: str
    oos_metrics: dict[str, float] = Field(
        default_factory=dict,
        description="Walk-forward or purged OOS only; do not use in-sample PnL here",
    )
