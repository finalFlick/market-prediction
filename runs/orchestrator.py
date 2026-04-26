"""Run lifecycle coordinator (Component 3 — minimal MVP-0 surface)."""

from __future__ import annotations

import asyncio
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import duckdb

from backtests.manifest import git_commit
from data.db import connect
from execution.brokers.base import Broker
from execution.reconciler import reconcile_brokers
from monitoring.logger import get_logger
from runs.exceptions import LiveTriggerForbidden
from runs.isolation import assert_run_context
from runs.recovery import transition_open_runs_to_failed
from runs.types import RunConfig

log = get_logger(__name__)

RUN_ROOT = Path("runs")


def _insert_run(
    conn: duckdb.DuckDBPyConnection,
    cfg: RunConfig,
    *,
    status: str = "queued",
) -> None:
    assert_run_context(None)  # submit is always system-level (no active run)
    payload = json.loads(cfg.model_dump_json())
    conn.execute(
        """
        INSERT OR REPLACE INTO runs (
            run_id, parent_run_id, experiment_id, run_type, mode, status,
            config_json, config_hash, git_commit, artifact_dir, error_reason,
            started_at, finished_at
        ) VALUES (?, NULL, NULL, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL)
        """,
        [
            cfg.run_id,
            cfg.run_type,
            cfg.mode,
            status,
            json.dumps(payload, sort_keys=True),
            cfg.config_hash(),
            git_commit(),
        ],
    )


class RunOrchestrator:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self._db_path = db_path

    def submit(self, config: RunConfig) -> str:
        if config.mode == "live" and config.trigger_is_ai:
            raise LiveTriggerForbidden("AI cannot trigger live runs")
        conn = connect(self._db_path)
        _insert_run(conn, config, status="queued")
        conn.close()
        log.info("run.submit", run_id=config.run_id, run_type=config.run_type, mode=config.mode)
        return config.run_id

    def on_boot(
        self,
        brokers: Sequence[Broker] | None = None,
    ) -> tuple[int, list[Any]]:
        n = transition_open_runs_to_failed(self._db_path, reason="container_restart")
        log.warning("run.recovery", transitioned=n, reason="container_restart")
        if not brokers:
            return n, []
        reports = asyncio.run(reconcile_brokers(brokers))
        return n, reports

    def list_runs(
        self,
        *,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        conn = connect(self._db_path)
        rows = conn.execute(
            """
            SELECT
                run_id,
                run_type,
                mode,
                status,
                config_hash,
                git_commit,
                started_at,
                finished_at,
                error_reason
            FROM runs ORDER BY run_id DESC LIMIT ?
            """,
            [int(limit)],
        ).fetchall()
        conn.close()
        keys = (
            "run_id",
            "run_type",
            "mode",
            "status",
            "config_hash",
            "git_commit",
            "started_at",
            "finished_at",
            "error_reason",
        )
        return [dict(zip(keys, r, strict=True)) for r in rows]

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        conn = connect(self._db_path)
        r = conn.execute(
            """
            SELECT
                run_id,
                run_type,
                mode,
                status,
                config_json,
                config_hash,
                git_commit,
                started_at,
                finished_at,
                error_reason,
                artifact_dir
            FROM runs WHERE run_id = ?
            """,
            [run_id],
        ).fetchone()
        conn.close()
        if r is None:
            return None
        keys = (
            "run_id",
            "run_type",
            "mode",
            "status",
            "config_json",
            "config_hash",
            "git_commit",
            "started_at",
            "finished_at",
            "error_reason",
            "artifact_dir",
        )
        return dict(zip(keys, r, strict=True))
