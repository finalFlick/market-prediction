"""Event bus contract (MVP-0)."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class EventBus(Protocol):
    def publish(
        self,
        stream: str,
        event_id: str,
        natural_key: str,
        payload: dict[str, Any],
    ) -> None: ...

    def read_stream(self, stream: str) -> list[tuple[str, str, dict[str, Any]]]:
        """Return ``(event_id, natural_key, payload)`` pairs (oldest first)."""
