"""Choose Redis or in-memory event transport."""

from __future__ import annotations

import os

from runs.events.in_memory import InMemoryEventBus
from runs.events.protocols import EventBus
from runs.events.redis_bus import RedisEventBus


def get_event_bus() -> EventBus:
    """Return a live Redis bus when ``REDIS_URL`` is set and reachable; else in-memory."""
    url = (os.getenv("REDIS_URL") or "").strip()
    if not url:
        return InMemoryEventBus()
    try:
        return RedisEventBus(url)
    except Exception:
        return InMemoryEventBus()
