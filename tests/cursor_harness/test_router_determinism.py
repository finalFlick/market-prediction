"""Determinism: same inputs → byte-identical ``additional_context``."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast


def test_route_deterministic(project_dir: Path) -> None:
    from _router_core import route
    from _router_types import LastPromptRecord, RoutingTable, SessionMemoryFile

    (project_dir / "AGENTS.md").write_text("body line", encoding="utf-8")
    table: dict[str, Any] = {
        "version": 1,
        "rules": [
            {
                "id": "r1",
                "priority": 1,
                "description": "",
                "match": {"prompt_regex": ["thing"]},
                "snippets": [{"path": "AGENTS.md", "anchor": None, "max_chars": 100}],
            }
        ],
    }
    last = {
        "session_id": "S1",
        "prompt": "fix the thing",
        "attachments": [],
        "captured_at": "2026-04-25T12:00:00+00:00",
    }
    now = datetime(2026, 4, 25, 12, 0, tzinfo=timezone.utc)

    text1, _, log1 = route(
        hook_input={"tool_name": "Read", "tool_input": {}, "tool_output": ""},
        last_prompt=cast(LastPromptRecord, last),
        routing_table=cast(RoutingTable, table),
        session_memory=cast(SessionMemoryFile, {"version": 1, "sessions": {}}),
        budget_chars=3000,
        project_dir=project_dir,
        now=now,
    )
    text2, _, log2 = route(
        hook_input={"tool_name": "Read", "tool_input": {}, "tool_output": ""},
        last_prompt=cast(LastPromptRecord, last),
        routing_table=cast(RoutingTable, table),
        session_memory=cast(SessionMemoryFile, {"version": 1, "sessions": {}}),
        budget_chars=3000,
        project_dir=project_dir,
        now=now,
    )
    assert text1 == text2
    assert log1 == log2
