"""Lightweight in-process gauges and counters.

Intentionally not Prometheus or StatsD yet; this is a thin facade so the rest
of the codebase can call `metrics.gauge("equity", v)` from day one. Swap the
backend later without changing call sites.
"""

from __future__ import annotations

import threading
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from monitoring.logger import get_logger

log = get_logger(__name__)


@dataclass
class _Registry:
    gauges: dict[str, float] = field(default_factory=dict)
    counters: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    lock: threading.Lock = field(default_factory=threading.Lock)


_registry = _Registry()


def gauge(name: str, value: float, **tags: Any) -> None:
    """Record a point-in-time value (e.g. equity, exposure)."""
    with _registry.lock:
        _registry.gauges[_key(name, tags)] = value
    log.debug("metric.gauge", name=name, value=value, **tags)


def counter(name: str, value: float = 1.0, **tags: Any) -> None:
    """Add to a monotonic counter (e.g. orders_placed)."""
    with _registry.lock:
        _registry.counters[_key(name, tags)] += value
    log.debug("metric.counter", name=name, value=value, **tags)


def snapshot() -> Mapping[str, float]:
    """Return a copy of the current registry, gauges and counters merged."""
    with _registry.lock:
        return {**_registry.gauges, **_registry.counters}


def _key(name: str, tags: Mapping[str, Any]) -> str:
    if not tags:
        return name
    suffix = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
    return f"{name}{{{suffix}}}"
