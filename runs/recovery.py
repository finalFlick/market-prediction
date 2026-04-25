"""Fail-closed on container restart (Day-0 Invariant 6, DD8)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path

import duckdb

from data.db import connect


def transition_open_runs_to_failed(
    path: str | Path | None = None,
    *,
    reason: str = "container_restart",
) -> int:
    """Return number of runs transitioned.

    `queued`, `running`, and `paused` → `failed` with ``error_reason`` set.
    """
    conn: duckdb.DuckDBPyConnection = connect(path)
    opened = "SELECT run_id, status FROM runs WHERE status IN ('queued','running','paused')"
    rows = conn.execute(opened).fetchall()
    n = 0
    for run_id, _st in rows:
        conn.execute(
            """
            UPDATE runs SET status = 'failed', error_reason = ?, finished_at = ?
            WHERE run_id = ?
            """,
            [reason, datetime.now(tz=UTC), str(run_id)],
        )
        conn.execute(
            """
            INSERT INTO state_transitions (
                st_id, run_id, from_status, to_status, reason, actor, transitioned_at
            )
            VALUES (?, ?, ?, 'failed', ?, 'system', ?)
            """,
            [
                str(uuid.uuid4()),
                str(run_id),
                str(_st),
                reason,
                datetime.now(tz=UTC),
            ],
        )
        n += 1
    conn.close()
    return n
