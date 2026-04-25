"""In-memory event bus (no Redis)."""

from __future__ import annotations

import pytest

from runs.events import InMemoryEventBus, get_event_bus


def test_in_memory_publish_read() -> None:
    b = InMemoryEventBus()
    b.publish("runs:ev", "e1", "n1", {"x": 1})
    b.publish("runs:ev", "e2", "n2", {"x": 2})
    rows = b.read_stream("runs:ev")
    assert len(rows) == 2
    assert rows[0] == ("e1", "n1", {"x": 1})
    assert rows[1] == ("e2", "n2", {"x": 2})


def test_get_event_bus_falls_back_without_redis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("REDIS_URL", raising=False)
    bus = get_event_bus()
    assert isinstance(bus, InMemoryEventBus)
