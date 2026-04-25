"""Append-only hash-chained rows (Day-0 Invariant 4; design § Compliance)."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

import duckdb

from monitoring.canonical_json import canonical_dumps

GENESIS_PREV = "0" * 64

CRITICAL_TABLES: frozenset[str] = frozenset(
    {
        "ha_orders",
        "ha_fills",
        "ha_risk_decisions",
        "ha_approvals",
        "ha_config_history",
    }
)


def _next_seq(conn: duckdb.DuckDBPyConnection, table: str) -> int:
    r = conn.execute(f"SELECT COALESCE(MAX(seq), 0) FROM {table}").fetchone()
    return int(r[0]) + 1 if r is not None else 1


def append_row(
    conn: duckdb.DuckDBPyConnection,
    table: str,
    *,
    natural_key: str,
    payload: dict[str, Any],
    run_id: str | None = None,
) -> str:
    """Insert one row; returns ``record_hash``."""
    if table not in CRITICAL_TABLES:
        msg = f"unknown hash-chain table: {table!r}"
        raise ValueError(msg)
    body = canonical_dumps(payload)
    last = conn.execute(f"SELECT record_hash FROM {table} ORDER BY seq DESC LIMIT 1").fetchone()
    prev_col = GENESIS_PREV if last is None else str(last[0])
    rec_hash = hashlib.sha256((prev_col + body).encode("utf-8")).hexdigest()
    seq = _next_seq(conn, table)
    ts = datetime.now(tz=UTC)
    conn.execute(
        f"""
        INSERT INTO {table} (
            seq, natural_key, run_id, payload_json, prev_hash, record_hash, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [seq, natural_key, run_id, body, prev_col, rec_hash, ts],
    )
    return rec_hash
