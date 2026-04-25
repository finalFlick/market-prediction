"""Schema regression for ``.cursor/hooks.json`` after wiring the router."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOKS_JSON = ROOT / ".cursor" / "hooks.json"


def _hooks() -> dict:
    return json.loads(HOOKS_JSON.read_text(encoding="utf-8"))


def test_hooks_json_parses_and_has_version() -> None:
    data = _hooks()
    assert data["version"] == 1


def test_before_submit_prompt_includes_capture_hook() -> None:
    data = _hooks()
    entries = data["hooks"].get("beforeSubmitPrompt", [])
    matching = [e for e in entries if "prompt_capture.py" in e["command"]]
    assert len(matching) == 1
    assert matching[0].get("timeout") == 5
    assert matching[0].get("failClosed") is not True


def test_post_tool_use_includes_router_hook() -> None:
    data = _hooks()
    entries = data["hooks"].get("postToolUse", [])
    matching = [e for e in entries if "prompt_context_router.py" in e["command"]]
    assert len(matching) == 1
    assert matching[0].get("timeout") == 5
    assert matching[0].get("failClosed") is not True


def test_existing_hooks_untouched() -> None:
    data = _hooks()
    sess = data["hooks"]["sessionStart"]
    assert any("session_init.py" in e["command"] for e in sess)
    assert any("spec-session-init.js" in e["command"] for e in sess)
    assert "block_dangerous_shell.py" in json.dumps(data["hooks"]["beforeShellExecution"])
