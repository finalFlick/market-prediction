"""Tests for ``_router_core.prune_memory``."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import cast


def test_prune_drops_expired_entries() -> None:
    from _router_core import prune_memory
    from _router_types import SessionMemoryFile

    now = datetime(2026, 4, 25, 12, 0, tzinfo=timezone.utc)
    fresh = (now - timedelta(hours=1)).isoformat()
    stale = (now - timedelta(hours=48)).isoformat()

    fresh_entry = {
        "rule_id": "a",
        "path": "x.md",
        "anchor": None,
        "sha256": "1",
        "injected_at": fresh,
    }
    stale_entry = {
        "rule_id": "b",
        "path": "y.md",
        "anchor": None,
        "sha256": "2",
        "injected_at": stale,
    }
    memory = cast(
        SessionMemoryFile,
        {"version": 1, "sessions": {"S1": [fresh_entry, stale_entry]}},
    )
    pruned = prune_memory(memory, now=now)
    entries = pruned["sessions"]["S1"]
    assert len(entries) == 1
    assert entries[0]["rule_id"] == "a"


def test_prune_drops_empty_sessions() -> None:
    from _router_core import prune_memory
    from _router_types import SessionMemoryFile

    now = datetime(2026, 4, 25, 12, 0, tzinfo=timezone.utc)
    stale = (now - timedelta(hours=48)).isoformat()
    stale_entry = {
        "rule_id": "b",
        "path": "y.md",
        "anchor": None,
        "sha256": "2",
        "injected_at": stale,
    }
    memory = cast(
        SessionMemoryFile,
        {"version": 1, "sessions": {"S1": [stale_entry]}},
    )
    pruned = prune_memory(memory, now=now)
    assert pruned["sessions"] == {}


def test_prune_keeps_unparseable_timestamps() -> None:
    """Defensive: a malformed timestamp should not nuke a session;
    we keep the entry rather than risk losing dedup state on a bad write."""
    from _router_core import prune_memory
    from _router_types import SessionMemoryFile

    now = datetime(2026, 4, 25, 12, 0, tzinfo=timezone.utc)
    bad_entry = {
        "rule_id": "a",
        "path": "x.md",
        "anchor": None,
        "sha256": "1",
        "injected_at": "garbage",
    }
    memory = cast(
        SessionMemoryFile,
        {"version": 1, "sessions": {"S1": [bad_entry]}},
    )
    pruned = prune_memory(memory, now=now)
    assert pruned["sessions"]["S1"]
