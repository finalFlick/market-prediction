"""Tests for ``_router_core.route`` — happy path, dedup, budget, dedup invalidate."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast


def _table(*rules: dict[str, Any]) -> dict[str, Any]:
    return {"version": 1, "rules": list(rules)}


def _last_prompt(prompt: str = "do the thing", session_id: str = "S1") -> dict[str, Any]:
    return {
        "session_id": session_id,
        "prompt": prompt,
        "attachments": [],
        "captured_at": datetime.now(tz=timezone.utc).isoformat(),
    }


def _empty_memory() -> dict[str, Any]:
    return {"version": 1, "sessions": {}}


def _now() -> datetime:
    return datetime(2026, 4, 25, 12, 0, tzinfo=timezone.utc)


def test_route_no_match_returns_empty_string(project_dir: Path) -> None:
    from _router_core import route
    from _router_types import LastPromptRecord, RoutingTable, SessionMemoryFile

    (project_dir / "AGENTS.md").write_text("body", encoding="utf-8")

    table = _table(
        {
            "id": "r1",
            "priority": 1,
            "description": "",
            "match": {"prompt_regex": ["nevermatch"]},
            "snippets": [{"path": "AGENTS.md", "anchor": None, "max_chars": 100}],
        }
    )
    text, _, log = route(
        hook_input={"tool_name": "Read", "tool_input": {}, "tool_output": ""},
        last_prompt=cast(LastPromptRecord, _last_prompt()),
        routing_table=cast(RoutingTable, table),
        session_memory=cast(SessionMemoryFile, _empty_memory()),
        budget_chars=3000,
        project_dir=project_dir,
        now=_now(),
    )
    assert text == ""
    assert log["matched_rule_ids"] == []


def test_route_match_injects_with_header(project_dir: Path) -> None:
    from _router_core import route
    from _router_types import LastPromptRecord, RoutingTable, SessionMemoryFile

    (project_dir / "AGENTS.md").write_text("body line", encoding="utf-8")

    table = _table(
        {
            "id": "r1",
            "priority": 1,
            "description": "",
            "match": {"prompt_regex": ["thing"]},
            "snippets": [{"path": "AGENTS.md", "anchor": None, "max_chars": 100}],
        }
    )
    text, mem, log = route(
        hook_input={"tool_name": "Read", "tool_input": {}, "tool_output": ""},
        last_prompt=cast(LastPromptRecord, _last_prompt("fix the thing")),
        routing_table=cast(RoutingTable, table),
        session_memory=cast(SessionMemoryFile, _empty_memory()),
        budget_chars=3000,
        project_dir=project_dir,
        now=_now(),
    )
    assert text.startswith("## Auto-loaded: AGENTS.md (rule: r1)")
    assert "body line" in text
    assert log["matched_rule_ids"] == ["r1"]
    assert "S1" in mem["sessions"]
    assert mem["sessions"]["S1"][0]["rule_id"] == "r1"


def test_route_dedup_skips_second_injection(project_dir: Path) -> None:
    from _router_core import route
    from _router_types import LastPromptRecord, RoutingTable, SessionMemoryFile

    (project_dir / "AGENTS.md").write_text("body line", encoding="utf-8")

    table = _table(
        {
            "id": "r1",
            "priority": 1,
            "description": "",
            "match": {"prompt_regex": ["x"]},
            "snippets": [{"path": "AGENTS.md", "anchor": None, "max_chars": 100}],
        }
    )
    args: dict[str, Any] = {
        "hook_input": {"tool_name": "Read", "tool_input": {}, "tool_output": ""},
        "last_prompt": cast(LastPromptRecord, _last_prompt("x")),
        "routing_table": cast(RoutingTable, table),
        "budget_chars": 3000,
        "project_dir": project_dir,
        "now": _now(),
    }
    text1, mem1, _ = route(session_memory=cast(SessionMemoryFile, _empty_memory()), **args)
    assert text1
    text2, _, log2 = route(session_memory=mem1, **args)
    assert text2 == ""
    assert log2["skip_reason"] == "deduplicated"


def test_route_dedup_invalidates_on_content_change(project_dir: Path) -> None:
    from _router_core import route
    from _router_types import LastPromptRecord, RoutingTable, SessionMemoryFile

    (project_dir / "AGENTS.md").write_text("first version", encoding="utf-8")

    table = _table(
        {
            "id": "r1",
            "priority": 1,
            "description": "",
            "match": {"prompt_regex": ["x"]},
            "snippets": [{"path": "AGENTS.md", "anchor": None, "max_chars": 100}],
        }
    )
    base_args: dict[str, Any] = {
        "hook_input": {"tool_name": "Read", "tool_input": {}, "tool_output": ""},
        "last_prompt": cast(LastPromptRecord, _last_prompt("x")),
        "routing_table": cast(RoutingTable, table),
        "budget_chars": 3000,
        "project_dir": project_dir,
        "now": _now(),
    }
    text1, mem1, _ = route(session_memory=cast(SessionMemoryFile, _empty_memory()), **base_args)
    assert text1

    (project_dir / "AGENTS.md").write_text("second version", encoding="utf-8")
    text2, _, log2 = route(session_memory=mem1, **base_args)
    assert text2 != ""
    assert "second version" in text2
    assert log2["skip_reason"] is None


def test_route_budget_drops_lowest_priority(project_dir: Path) -> None:
    from _router_core import route
    from _router_types import LastPromptRecord, RoutingTable, SessionMemoryFile

    big = "Z" * 800
    (project_dir / "high.md").write_text(big, encoding="utf-8")
    (project_dir / "low.md").write_text(big, encoding="utf-8")

    table = _table(
        {
            "id": "high",
            "priority": 100,
            "description": "",
            "match": {"prompt_regex": ["x"]},
            "snippets": [{"path": "high.md", "anchor": None, "max_chars": 1000}],
        },
        {
            "id": "low",
            "priority": 1,
            "description": "",
            "match": {"prompt_regex": ["x"]},
            "snippets": [{"path": "low.md", "anchor": None, "max_chars": 1000}],
        },
    )
    text, _, log = route(
        hook_input={"tool_name": "Read", "tool_input": {}, "tool_output": ""},
        last_prompt=cast(LastPromptRecord, _last_prompt("x")),
        routing_table=cast(RoutingTable, table),
        session_memory=cast(SessionMemoryFile, _empty_memory()),
        budget_chars=900,
        project_dir=project_dir,
        now=_now(),
    )
    assert "high.md" in text
    assert "low.md" not in text
    assert log["matched_rule_ids"] == ["high", "low"]
    assert [s["path"] for s in log["injected_snippets"]] == ["high.md"]


def test_route_per_snippet_truncation_applied(project_dir: Path) -> None:
    from _router_core import route
    from _router_types import LastPromptRecord, RoutingTable, SessionMemoryFile

    (project_dir / "doc.md").write_text("Q" * 5000, encoding="utf-8")
    table = _table(
        {
            "id": "r1",
            "priority": 1,
            "description": "",
            "match": {"prompt_regex": ["x"]},
            "snippets": [{"path": "doc.md", "anchor": None, "max_chars": 200}],
        }
    )
    text, _, _ = route(
        hook_input={"tool_name": "Read", "tool_input": {}, "tool_output": ""},
        last_prompt=cast(LastPromptRecord, _last_prompt("x")),
        routing_table=cast(RoutingTable, table),
        session_memory=cast(SessionMemoryFile, _empty_memory()),
        budget_chars=3000,
        project_dir=project_dir,
        now=_now(),
    )
    assert "[truncated]" in text


def test_route_zero_budget_returns_empty(project_dir: Path) -> None:
    from _router_core import route
    from _router_types import LastPromptRecord, RoutingTable, SessionMemoryFile

    (project_dir / "AGENTS.md").write_text("x", encoding="utf-8")
    table = _table(
        {
            "id": "r",
            "priority": 1,
            "description": "",
            "match": {"prompt_regex": ["x"]},
            "snippets": [{"path": "AGENTS.md", "anchor": None, "max_chars": 100}],
        }
    )
    text, _, _ = route(
        hook_input={"tool_name": "Read", "tool_input": {}, "tool_output": ""},
        last_prompt=cast(LastPromptRecord, _last_prompt("x")),
        routing_table=cast(RoutingTable, table),
        session_memory=cast(SessionMemoryFile, _empty_memory()),
        budget_chars=0,
        project_dir=project_dir,
        now=_now(),
    )
    assert text == ""


def test_route_missing_snippet_skipped(project_dir: Path) -> None:
    from _router_core import route
    from _router_types import LastPromptRecord, RoutingTable, SessionMemoryFile

    (project_dir / "good.md").write_text("good", encoding="utf-8")
    table = _table(
        {
            "id": "r",
            "priority": 1,
            "description": "",
            "match": {"prompt_regex": ["x"]},
            "snippets": [
                {"path": "absent.md", "anchor": None, "max_chars": 100},
                {"path": "good.md", "anchor": None, "max_chars": 100},
            ],
        }
    )
    text, _, _ = route(
        hook_input={"tool_name": "Read", "tool_input": {}, "tool_output": ""},
        last_prompt=cast(LastPromptRecord, _last_prompt("x")),
        routing_table=cast(RoutingTable, table),
        session_memory=cast(SessionMemoryFile, _empty_memory()),
        budget_chars=3000,
        project_dir=project_dir,
        now=_now(),
    )
    assert "good" in text
    assert "absent.md" not in text
