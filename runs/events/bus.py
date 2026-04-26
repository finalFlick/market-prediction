"""Single publish facade: Redis Streams xadd + DuckDB outbox in one call (Inv-7).

All code that emits run events MUST call ``publish_event`` (or the
``EventPublisher`` class) instead of accessing ``redis.Redis`` or
``xadd`` directly.  An AST guard in ``tests/security/test_direct_redis_use.py``
enforces this.

The function writes the DuckDB outbox row first (durable), then xadd to Redis
(best-effort).  If Redis is unavailable the event is still safely in DuckDB and
will be replayed by the consumer.  Consumers are idempotent by ``event_id``
(``INSERT OR IGNORE`` in the outbox table).
"""

from __future__ import annotations

import os
from typing import Any

import duckdb

from runs.events.outbox import write_outbox


class EventPublisher:
    """Publish events durably to DuckDB, optionally fanning out to Redis.

    Parameters
    ----------
    db_conn:
        Open DuckDB connection that owns ``run_events_durable``.
    redis_url:
        Redis URL.  When *None* (default) the env var ``REDIS_URL`` is checked;
        if absent the Redis step is skipped silently.
    """

    def __init__(
        self,
        db_conn: duckdb.DuckDBPyConnection,
        *,
        redis_url: str | None = None,
    ) -> None:
        self._conn = db_conn
        url = redis_url if redis_url is not None else (os.getenv("REDIS_URL") or "").strip()
        self._redis: Any = None
        if url:
            try:
                import redis  # noqa: PLC0415

                self._redis = redis.Redis.from_url(url, socket_timeout=2.0, decode_responses=True)
                self._redis.ping()
            except Exception:
                self._redis = None

    def publish(
        self,
        stream: str,
        event_id: str,
        natural_key: str,
        payload: dict[str, Any],
    ) -> bool:
        """Write the event to DuckDB and optionally to Redis Streams.

        Returns ``True`` if a new outbox row was inserted (``False`` on dedup).
        Redis delivery is best-effort; a failure there does not raise.
        """
        import json  # noqa: PLC0415

        inserted = write_outbox(
            self._conn,
            stream=stream,
            event_id=event_id,
            natural_key=natural_key,
            payload=payload,
        )
        if self._redis is not None:
            import contextlib  # noqa: PLC0415

            with contextlib.suppress(Exception):
                self._redis.xadd(
                    stream,
                    {
                        "event_id": event_id,
                        "natural_key": natural_key,
                        "payload": json.dumps(payload, sort_keys=True, default=str),
                    },
                )
        return inserted


def publish_event(
    db_conn: duckdb.DuckDBPyConnection,
    stream: str,
    event_id: str,
    natural_key: str,
    payload: dict[str, Any],
    *,
    redis_url: str | None = None,
) -> bool:
    """Module-level convenience wrapper around :class:`EventPublisher`.

    Prefer this for one-shot calls; instantiate ``EventPublisher`` when you
    need to publish multiple events on the same connection.
    """
    pub = EventPublisher(db_conn, redis_url=redis_url)
    return pub.publish(stream, event_id, natural_key, payload)
