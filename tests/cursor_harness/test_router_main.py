"""Tests for ``.cursor/hooks/prompt_context_router.py`` entry point."""

from __future__ import annotations

import importlib
import io
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


def _seed_routing_table(project_dir: Path, rules: list[dict]) -> None:
    table = {"version": 1, "rules": rules}
    (project_dir / ".cursor" / "context-router.json").write_text(
        json.dumps(table), encoding="utf-8"
    )


def _seed_last_prompt(project_dir: Path, prompt: str, *, age_minutes: int = 1) -> None:
    captured_at = (datetime.now(tz=timezone.utc) - timedelta(minutes=age_minutes)).isoformat()
    (project_dir / ".cursor" / "state" / "last-prompt.json").write_text(
        json.dumps(
            {
                "session_id": "S1",
                "prompt": prompt,
                "attachments": [],
                "captured_at": captured_at,
            }
        ),
        encoding="utf-8",
    )


def _run_main(payload: dict, monkeypatch: pytest.MonkeyPatch) -> tuple[str, str]:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    out = io.StringIO()
    err = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)
    if "prompt_context_router" in sys.modules:
        del sys.modules["prompt_context_router"]
    mod = importlib.import_module("prompt_context_router")
    mod.main()
    return out.getvalue(), err.getvalue()


def test_router_happy_path_injects(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (project_dir / "AGENTS.md").write_text("agents content", encoding="utf-8")
    _seed_routing_table(
        project_dir,
        [
            {
                "id": "agents",
                "priority": 1,
                "match": {"prompt_regex": ["agents"]},
                "snippets": [{"path": "AGENTS.md", "anchor": None, "max_chars": 100}],
            }
        ],
    )
    _seed_last_prompt(project_dir, "tell me about the agents")

    out, _err = _run_main(
        {"tool_name": "Read", "tool_input": {"path": "AGENTS.md"}, "tool_output": ""},
        monkeypatch,
    )
    payload = json.loads(out)
    assert "additional_context" in payload
    assert "agents content" in payload["additional_context"]
    assert (project_dir / ".cursor" / "state" / "session-context-memory.json").exists()
    assert (project_dir / ".cursor" / "state" / "router-log.jsonl").exists()


def test_router_no_match_returns_empty(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (project_dir / "AGENTS.md").write_text("x", encoding="utf-8")
    _seed_routing_table(
        project_dir,
        [
            {
                "id": "x",
                "priority": 1,
                "match": {"prompt_regex": ["nope"]},
                "snippets": [{"path": "AGENTS.md", "anchor": None, "max_chars": 100}],
            }
        ],
    )
    _seed_last_prompt(project_dir, "totally unrelated")

    out, _err = _run_main(
        {"tool_name": "Read", "tool_input": {"path": "x.py"}, "tool_output": ""},
        monkeypatch,
    )
    assert json.loads(out) == {}


def test_router_stale_prompt_ignored(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (project_dir / "AGENTS.md").write_text("x", encoding="utf-8")
    _seed_routing_table(
        project_dir,
        [
            {
                "id": "r",
                "priority": 1,
                "match": {"prompt_regex": ["agents"]},
                "snippets": [{"path": "AGENTS.md", "anchor": None, "max_chars": 100}],
            }
        ],
    )
    _seed_last_prompt(project_dir, "agents are great", age_minutes=999)

    out, _err = _run_main(
        {"tool_name": "Read", "tool_input": {"path": "x.py"}, "tool_output": ""},
        monkeypatch,
    )
    assert json.loads(out) == {}


def test_router_missing_routing_table_returns_empty(
    project_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out, _err = _run_main(
        {"tool_name": "Read", "tool_input": {}, "tool_output": ""},
        monkeypatch,
    )
    assert json.loads(out) == {}


def test_router_disabled_env_short_circuits(
    project_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TLAB_ROUTER_DISABLE", "true")
    (project_dir / "AGENTS.md").write_text("x", encoding="utf-8")
    _seed_routing_table(
        project_dir,
        [
            {
                "id": "r",
                "priority": 1,
                "match": {"prompt_regex": [".*"]},
                "snippets": [{"path": "AGENTS.md", "anchor": None, "max_chars": 100}],
            }
        ],
    )
    _seed_last_prompt(project_dir, "x")
    out, _err = _run_main(
        {"tool_name": "Read", "tool_input": {}, "tool_output": ""},
        monkeypatch,
    )
    assert json.loads(out) == {}


def test_router_budget_env_override(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TLAB_ROUTER_BUDGET_CHARS", "10")
    (project_dir / "AGENTS.md").write_text("Q" * 5000, encoding="utf-8")
    _seed_routing_table(
        project_dir,
        [
            {
                "id": "r",
                "priority": 1,
                "match": {"prompt_regex": [".*"]},
                "snippets": [{"path": "AGENTS.md", "anchor": None, "max_chars": 1000}],
            }
        ],
    )
    _seed_last_prompt(project_dir, "x")
    out, _err = _run_main(
        {"tool_name": "Read", "tool_input": {}, "tool_output": ""},
        monkeypatch,
    )
    payload = json.loads(out)
    assert payload == {} or len(payload.get("additional_context", "")) <= 10
