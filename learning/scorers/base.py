"""`Scorer` protocol — OOS `RunSummary` only."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from learning.types import RunSummary


@runtime_checkable
class Scorer(Protocol):
    name: str

    def update(self, summary: RunSummary) -> None: ...


def assert_oos_only(summary: RunSummary) -> None:
    if not summary.oos_metrics:
        raise ValueError("oos_metrics must be non-empty for OOS-only scoring")
