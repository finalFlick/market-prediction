"""Four MVP-0 levers: strategy, source, feature, llm-calibration (minimal heuristics)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

import duckdb

from data.db import connect
from learning.scorers.base import Scorer, assert_oos_only
from learning.types import RunSummary
from runs.isolation import assert_run_context


@dataclass
class _Scorer:
    name: str
    level: str
    _path: str | None = field(default=None, repr=False)

    def update(self, summary: RunSummary) -> None:
        assert_oos_only(summary)
        assert_run_context(summary.run_id)
        sharpe = float(summary.oos_metrics.get("sharpe", 0.0))
        key = "momentum_baseline"
        p = self._path
        con = connect(p) if p is not None else connect()
        ts = datetime.now(tz=UTC)
        con.execute(
            """
            INSERT OR REPLACE INTO scoreboard (level, key, score, weight, last_run_id, updated_at)
            VALUES (?, ?, ?, 1.0, ?, ?)
            """,
            [self.level, key, sharpe, summary.run_id, ts],
        )
        con.close()


@dataclass
class SourceScorer:
    name: str = "source"
    level: str = "source"
    _path: str | None = field(default=None, repr=False)

    def update(self, summary: RunSummary) -> None:
        assert_oos_only(summary)
        assert_run_context(summary.run_id)
        dd = float(summary.oos_metrics.get("max_drawdown", 0.0))
        score = -dd
        p = self._path
        con: duckdb.DuckDBPyConnection = connect(p) if p is not None else connect()
        ts = datetime.now(tz=UTC)
        con.execute(
            """
            INSERT OR REPLACE INTO scoreboard (level, key, score, weight, last_run_id, updated_at)
            VALUES ('source', 'crypto_binance', ?, 1.0, ?, ?)
            """,
            [score, summary.run_id, ts],
        )
        con.close()


@dataclass
class FeatureScorer:
    name: str = "feature"
    level: str = "feature"
    _path: str | None = field(default=None, repr=False)

    def update(self, summary: RunSummary) -> None:
        assert_oos_only(summary)
        assert_run_context(summary.run_id)
        key = "momentum_bundle"
        score = float(summary.oos_metrics.get("hit_rate", 0.0))
        p = self._path
        con = connect(p) if p is not None else connect()
        ts = datetime.now(tz=UTC)
        con.execute(
            """
            INSERT OR REPLACE INTO scoreboard (level, key, score, weight, last_run_id, updated_at)
            VALUES ('feature', ?, ?, 1.0, ?, ?)
            """,
            [key, score, summary.run_id, ts],
        )
        con.close()


@dataclass
class LlmCalibrationScorer:
    name: str = "llm_calibration"
    level: str = "llm_calibration"
    _path: str | None = field(default=None, repr=False)

    def update(self, summary: RunSummary) -> None:
        assert_oos_only(summary)
        assert_run_context(summary.run_id)
        # MVP-0 proxy: use OOS hit_rate as a rough calibration signal.
        # weight=0.0 so this lever does not influence allocation yet
        # (task-type calibration is [v1] per design.md § AI/ML Design).
        score = float(summary.oos_metrics.get("hit_rate", 0.0))
        p = self._path
        con = connect(p) if p is not None else connect()
        ts = datetime.now(tz=UTC)
        con.execute(
            """
            INSERT OR REPLACE INTO scoreboard (level, key, score, weight, last_run_id, updated_at)
            VALUES ('llm_calibration', 'hit_rate_proxy', ?, 0.0, ?, ?)
            """,
            [score, summary.run_id, ts],
        )
        con.close()


def make_default_scorers(
    path: str | None = None,
) -> list[Scorer]:
    s = _Scorer(name="strategy", level="strategy", _path=path)
    return [
        s,
        SourceScorer(_path=path),
        FeatureScorer(_path=path),
        LlmCalibrationScorer(_path=path),
    ]


def apply_scorers(
    scorers: list[Scorer],
    summary: RunSummary,
) -> None:
    for s in scorers:
        s.update(summary)
