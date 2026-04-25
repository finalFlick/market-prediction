"""Process-local event bus (no Redis)."""

from __future__ import annotations

from collections import deque
from typing import Any


class InMemoryEventBus:
    """Append-only per-stream deque for dev and no-Redis deployments."""

    def __init__(self) -> None:
        self._streams: dict[str, deque[tuple[str, str, dict[str, Any]]]] = {}

    def publish(
        self,
        stream: str,
        event_id: str,
        natural_key: str,
        payload: dict[str, Any],
    ) -> None:
        q = self._streams.setdefault(stream, deque())
        q.append((event_id, natural_key, dict(payload)))

    def read_stream(self, stream: str) -> list[tuple[str, str, dict[str, Any]]]:
        q = self._streams.get(stream)
        if not q:
            return []
        return list(q)
