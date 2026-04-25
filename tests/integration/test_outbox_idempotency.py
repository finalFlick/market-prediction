"""Duplicate event_id does not double-insert (DD2)."""

from __future__ import annotations

from pathlib import Path

import pytest

from data.db import connect
from runs.events.outbox import write_outbox


@pytest.mark.integration
def test_outbox_duplicate_event_id_ignored(tmp_path: Path) -> None:
    p = tmp_path / "o.duckdb"
    c = connect(p)
    assert write_outbox(
        c,
        stream="runs:events",
        event_id="e1",
        natural_key="n1",
        payload={"a": 1},
    )
    assert not write_outbox(
        c,
        stream="runs:events",
        event_id="e1",
        natural_key="n1",
        payload={"a": 1},
    )
    c.close()
