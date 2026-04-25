"""Redis Streams-backed event bus."""

from __future__ import annotations

import json
from typing import Any, cast

import redis


class RedisEventBus:
    """Minimal ``XADD`` / ``XRANGE`` surface for cross-process fan-out."""

    def __init__(self, url: str) -> None:
        self._r = redis.Redis.from_url(url, socket_timeout=5.0, decode_responses=True)
        self._r.ping()

    def publish(
        self,
        stream: str,
        event_id: str,
        natural_key: str,
        payload: dict[str, Any],
    ) -> None:
        self._r.xadd(
            stream,
            {
                "event_id": event_id,
                "natural_key": natural_key,
                "payload": json.dumps(payload, sort_keys=True, default=str),
            },
        )

    def read_stream(self, stream: str) -> list[tuple[str, str, dict[str, Any]]]:
        raw: Any = self._r.xrange(stream, min="-", max="+", count=10_000)
        entries = cast(list[tuple[str, dict[str, str]]], list(raw))
        out: list[tuple[str, str, dict[str, Any]]] = []
        for _xid, fields in entries:
            if not isinstance(fields, dict):
                continue
            eid = str(fields.get("event_id", ""))
            nk = str(fields.get("natural_key", ""))
            raw = fields.get("payload", "{}")
            pl = json.loads(raw) if isinstance(raw, str) else {}
            out.append((eid, nk, pl))
        return out
