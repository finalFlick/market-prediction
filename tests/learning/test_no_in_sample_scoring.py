from __future__ import annotations

from pathlib import Path

import pytest

from learning.scorers.base import assert_oos_only
from learning.scorers.standard import apply_scorers, make_default_scorers
from learning.types import RunSummary


def test_scorer_rejects_empty_oos() -> None:
    with pytest.raises(ValueError, match="oos_metrics"):
        assert_oos_only(RunSummary(run_id="r1", oos_metrics={}))


def test_apply_scorers_runs_on_oos_only(tmp_path: Path) -> None:
    p = tmp_path / "d.duckdb"
    s = make_default_scorers(str(p))
    apply_scorers(
        s,
        RunSummary(run_id="r1", oos_metrics={"sharpe": 1.2, "max_drawdown": -0.1, "hit_rate": 0.5}),
    )
