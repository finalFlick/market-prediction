"""Shared DuckDB connection factory and schema bootstrapper."""

from __future__ import annotations

import os
from pathlib import Path

import duckdb

_SCHEMA_FILE = Path(__file__).with_name("schema.sql")


def default_path() -> Path:
    return Path(os.getenv("DUCKDB_PATH", "data/market.duckdb"))


def connect(path: str | Path | None = None) -> duckdb.DuckDBPyConnection:
    """Open a DuckDB connection and ensure the schema exists."""
    p = Path(path) if path else default_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(p))
    conn.execute(_SCHEMA_FILE.read_text())
    return conn
