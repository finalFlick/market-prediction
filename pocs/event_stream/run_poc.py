"""POC 4: in-memory Redis stand-in + durable outbox; replay after 'crash'.

Production: Redis + DuckDB. This POC uses **SQLite** (stdlib) for the outbox
when DuckDB is missing; same idempotency pattern.
"""

from __future__ import annotations

import json
import sqlite3
import tempfile
import uuid
from dataclasses import dataclass, field
from typing import Any

try:
    import duckdb
except ModuleNotFoundError:  # pragma: no cover
    duckdb = None  # type: ignore[misc, assignment]

try:
    import redis
except ImportError:  # pragma: no cover
    redis = None  # type: ignore[misc, assignment]


@dataclass
class InMemoryStream:
    _entries: list[tuple[str, str, str]] = field(default_factory=list)

    def xadd(self, name: str, fields: dict[str, str]) -> str:  # noqa: ARG002
        eid = f"{len(self._entries) + 1}-0"
        for k, v in fields.items():
            self._entries.append((eid, k, v))
        return eid


def connect_stream() -> Any:
    if redis is None:
        return InMemoryStream()
    r = redis.Redis(host="127.0.0.1", port=6379, decode_responses=True)
    try:
        r.ping()
    except (redis.exceptions.ConnectionError, OSError):
        return InMemoryStream()
    return r


def _db_connect(path: str) -> tuple[Any, str]:
    if duckdb is not None:
        con = duckdb.connect(path)  # type: ignore[union-attr]
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS outbox (
                stream_id TEXT,
                event_type TEXT,
                payload TEXT,
                natural_key TEXT PRIMARY KEY
            );
        """
        )
        return con, "duckdb"
    con2 = sqlite3.connect(path)
    con2.execute(
        """
        CREATE TABLE IF NOT EXISTS outbox (
            stream_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            payload TEXT NOT NULL,
            natural_key TEXT NOT NULL,
            PRIMARY KEY (natural_key)
        );
    """
    )
    con2.commit()
    return con2, "sqlite"


def _is_duckdb(con: Any) -> bool:
    if duckdb is None:
        return False
    mod = type(con).__module__
    return mod.startswith("duckdb")


def run_once(stream: Any, con: Any) -> set[str]:
    """Append events; idempotent on natural_key."""
    processed: set[str] = set()

    def emit(etype: str, payload: dict[str, Any]) -> None:
        pjson = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        )
        if isinstance(stream, InMemoryStream):
            sid = stream.xadd("trading:events", {"data": pjson, "type": etype})
        else:
            sid = str(
                stream.xadd(  # type: ignore[union-attr, unused-ignore]
                    "trading:events", {"data": pjson, "type": etype}
                )
            )
        sk = f"{etype}:{payload.get('order_id', payload.get('run_id', ''))}"
        if _is_duckdb(con):
            try:
                con.execute(  # type: ignore[union-attr]
                    "INSERT INTO outbox VALUES (?, ?, ?, ?)",
                    [str(sid), etype, pjson, sk],
                )
            except Exception:
                pass
        else:
            con.execute(
                "INSERT OR IGNORE INTO outbox (stream_id, event_type, payload, natural_key) VALUES (?, ?, ?, ?)",  # noqa: E501
                (str(sid), etype, pjson, sk),
            )
        processed.add(sk)
        if not _is_duckdb(con):
            con.commit()

    rid = str(uuid.uuid4())
    emit("run_started", {"run_id": rid})
    emit("signal_generated", {"run_id": rid, "asset": "AAPL", "z": 1.2})
    oid = str(uuid.uuid4())
    emit("order_submitted", {"run_id": rid, "order_id": oid})
    emit("order_filled", {"order_id": oid, "px": 150.0})
    return processed


def recover_replay(con: Any) -> set[str]:
    cur = con.execute("SELECT natural_key FROM outbox")  # type: ignore[union-attr, unused-ignore]
    rows = cur.fetchall()  # type: ignore[union-attr, unused-ignore]
    return {r[0] for r in rows}


def main() -> None:
    s = connect_stream()
    with tempfile.TemporaryDirectory() as td:
        path = f"{td}/o.db"
        con, backend = _db_connect(path)
        try:
            a = run_once(s, con)
            _ = InMemoryStream()  # lost "Redis" between processes
            b = recover_replay(con)
            assert a == b, f"{a!r} vs {b!r}"
            assert recover_replay(con) == a
        finally:
            con.close()  # Windows: release file before temp dir delete
    transport = "in_memory" if isinstance(s, InMemoryStream) else "redis"
    print(
        f"POC4_OK: outbox==replay; transport={transport}; store={backend} "
        "(DuckDB in full stack; SQLite OK for POC if no duckdb installed)"
    )


if __name__ == "__main__":
    main()
