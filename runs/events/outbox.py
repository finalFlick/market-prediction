"""Mirror Redis-style events to DuckDB for idempotency (DD2; ``run_events_durable``)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import duckdb

from data.db import connect


def write_outbox(
    conn: duckdb.DuckDBPyConnection,
    *,
    stream: str,
    event_id: str,
    natural_key: str,
    payload: dict[str, Any],
) -> bool:
    """Return True if a new row was written.

    False if deduplicated (duplicate event_id or natural key).
    """
    body = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    ts = datetime.now(tz=UTC)
    before_row = conn.execute("SELECT COUNT(*) FROM run_events_durable").fetchone()
    if before_row is None:
        msg = "count query returned no row"
        raise RuntimeError(msg)
    before = int(before_row[0])
    conn.execute(
        """
        INSERT OR IGNORE INTO run_events_durable (
            stream, event_id, natural_key, payload_json, created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        [stream, event_id, natural_key, body, ts],
    )
    after_row = conn.execute("SELECT COUNT(*) FROM run_events_durable").fetchone()
    if after_row is None:
        msg = "count query returned no row"
        raise RuntimeError(msg)
    after = int(after_row[0])
    return after > before


def append_with_connect(
    path: str | None,
    **kwargs: Any,
) -> bool:
    con: duckdb.DuckDBPyConnection = connect(path) if path else connect()
    out = write_outbox(con, **kwargs)
    con.close()
    return out
