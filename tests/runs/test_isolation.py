"""Day-0 Invariant 5: cross-run state writes raise RunIsolationViolation."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest

from data.db import connect
from data.repositories.audit.chain import append_row
from learning.scorers.standard import apply_scorers, make_default_scorers
from learning.types import RunSummary
from runs.exceptions import RunIsolationViolation
from runs.isolation import assert_run_context, bind_run_context, clear_run_context


@pytest.fixture(autouse=True)
def _clean_context() -> Generator[None, None, None]:
    clear_run_context()
    yield
    clear_run_context()


def test_assert_run_context_passes_when_no_active_context() -> None:
    assert_run_context("any-run-id")


def test_assert_run_context_passes_when_ids_match() -> None:
    bind_run_context(run_id="run-123")
    assert_run_context("run-123")


def test_assert_run_context_raises_when_ids_differ() -> None:
    bind_run_context(run_id="run-A")
    with pytest.raises(RunIsolationViolation, match="run-B"):
        assert_run_context("run-B")


def test_assert_run_context_passes_for_none_run_id() -> None:
    bind_run_context(run_id="run-A")
    assert_run_context(None)


def test_append_row_raises_isolation_with_wrong_run_id(tmp_path: Path) -> None:
    db = tmp_path / "iso.duckdb"
    conn = connect(db)
    bind_run_context(run_id="run-active")
    with pytest.raises(RunIsolationViolation):
        append_row(
            conn,
            "ha_risk_decisions",
            natural_key="d1",
            payload={"x": 1},
            run_id="run-other",
        )
    conn.close()


def test_append_row_succeeds_with_matching_run_id(tmp_path: Path) -> None:
    db = tmp_path / "iso2.duckdb"
    conn = connect(db)
    bind_run_context(run_id="run-match")
    h = append_row(
        conn,
        "ha_risk_decisions",
        natural_key="d1",
        payload={"x": 1},
        run_id="run-match",
    )
    assert h
    conn.close()


def test_scorer_raises_isolation_with_wrong_run_id(tmp_path: Path) -> None:
    bind_run_context(run_id="run-A")
    scorers = make_default_scorers(str(tmp_path / "s.duckdb"))
    summary = RunSummary(
        run_id="run-B",
        oos_metrics={"sharpe": 1.0, "max_drawdown": -0.05, "hit_rate": 0.6},
    )
    with pytest.raises(RunIsolationViolation):
        apply_scorers(scorers, summary)


def test_scorer_succeeds_with_matching_run_id(tmp_path: Path) -> None:
    bind_run_context(run_id="run-X")
    scorers = make_default_scorers(str(tmp_path / "s2.duckdb"))
    summary = RunSummary(
        run_id="run-X",
        oos_metrics={"sharpe": 0.9, "max_drawdown": -0.08, "hit_rate": 0.55},
    )
    apply_scorers(scorers, summary)
