"""Recompute and verify per-table hash chains."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import duckdb

from data.db import default_path
from data.repositories.audit.chain import CRITICAL_TABLES, GENESIS_PREV


def _resolve_path(db_path: str | Path | None) -> Path:
    p = Path(db_path) if db_path is not None else default_path()
    if not p.exists():
        msg = f"DuckDB file not found: {p}"
        raise FileNotFoundError(msg)
    return p


def verify_table(conn: duckdb.DuckDBPyConnection, table: str) -> tuple[bool, str]:
    """Return (ok, message). ``payload_json`` in DB is already canonical (string)."""
    rows = conn.execute(
        f"SELECT seq, prev_hash, record_hash, payload_json FROM {table} ORDER BY seq"
    ).fetchall()
    expected_prev = GENESIS_PREV
    for seq, prev_h, rec_h, payload in rows:
        raw = (
            bytes(payload).decode("utf-8")
            if isinstance(payload, bytes | memoryview)
            else str(payload)
        )
        p = str(prev_h)
        r = str(rec_h)
        b = raw
        if p != expected_prev:
            msg = (
                f"chain prev mismatch at seq={seq!r} table={table!r}: "
                f"got {p!r} want {expected_prev!r}"
            )
            return (False, msg)
        want = hashlib.sha256((p + b).encode("utf-8")).hexdigest()
        if r != want:
            return (
                False,
                f"record_hash mismatch at seq={seq!r} table={table!r}: got {r!r} want {want!r}",
            )
        expected_prev = r
    return True, f"ok {len(rows)} rows in {table}"


def verify_all(
    *,
    db_path: str | Path | None = None,
    tables: str = "critical",
) -> dict[str, Any]:
    if tables not in ("critical", "all"):
        msg = f"invalid tables option: {tables!r}"
        raise ValueError(msg)
    p = _resolve_path(db_path)
    conn = duckdb.connect(str(p), read_only=True)
    out: dict[str, Any] = {"db": str(p), "tables": {}}
    # MVP-0: `critical` and `all` are the same five tables; extend for v1+.
    names = list(CRITICAL_TABLES)
    all_ok = True
    for t in names:
        ok, msg = verify_table(conn, t)
        out["tables"][t] = {"ok": ok, "message": msg}
        all_ok = all_ok and ok
    conn.close()
    out["all_ok"] = all_ok
    return out
