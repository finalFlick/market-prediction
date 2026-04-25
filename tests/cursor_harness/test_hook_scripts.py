"""Smoke tests for `.cursor/hooks/*.py`.

Every hook script must:

1. Read JSON from stdin (we pipe a representative payload).
2. Either write valid JSON to stdout or write nothing.
3. Exit 0 (or 2 to deliberately block — we mark those tests).
4. Never raise an uncaught exception.

These tests are stdlib-only so they work in CI without docker.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = ROOT / ".cursor" / "hooks"
PYTHON = sys.executable

EXPECTED_DURATION_MS = 500


def _run_hook(script: str, stdin_payload: dict | None) -> tuple[int, str, str]:
    """Run a hook script and capture its stdout/stderr."""
    body = json.dumps(stdin_payload or {})
    env = {**os.environ, "CURSOR_PROJECT_DIR": str(ROOT)}
    proc = subprocess.run(
        [PYTHON, str(HOOKS_DIR / script)],
        input=body,
        text=True,
        capture_output=True,
        timeout=20,
        env=env,
        cwd=str(ROOT),
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _parse_stdout(stdout: str) -> dict:
    """Parse hook stdout as JSON; tolerate empty output."""
    s = stdout.strip()
    if not s:
        return {}
    return json.loads(s)


def test_session_init_returns_additional_context() -> None:
    rc, out, _err = _run_hook(
        "session_init.py",
        {"session_id": "test-1", "is_background_agent": False, "composer_mode": "agent"},
    )
    assert rc == 0
    payload = _parse_stdout(out)
    assert "additional_context" in payload
    assert "trading-lab" in payload["additional_context"].lower()


@pytest.mark.parametrize(
    "command",
    [
        "echo hello",
        "ls -la",
        "pytest -q",
        "git status",
    ],
)
def test_block_dangerous_shell_allows_safe_commands(command: str) -> None:
    rc, out, _err = _run_hook("block_dangerous_shell.py", {"command": command})
    assert rc == 0
    assert _parse_stdout(out)["permission"] == "allow"


@pytest.mark.parametrize(
    "command",
    [
        "rm -rf /",
        "rm -rf $HOME",
        "mkfs.ext4 /dev/sda1",
        "dd if=/dev/zero of=/dev/sda",
    ],
)
def test_block_dangerous_shell_denies_destructive(command: str) -> None:
    rc, out, _err = _run_hook("block_dangerous_shell.py", {"command": command})
    assert rc == 0
    assert _parse_stdout(out)["permission"] == "deny"


@pytest.mark.parametrize(
    "command",
    [
        "git push --force origin main",
        "docker compose down -v",
        "python -m execution.runner --broker binance",
    ],
)
def test_block_dangerous_shell_asks_for_risky(command: str) -> None:
    rc, out, _err = _run_hook("block_dangerous_shell.py", {"command": command})
    assert rc == 0
    assert _parse_stdout(out)["permission"] == "ask"


def test_guard_mcp_writes_allows_reads() -> None:
    rc, out, _err = _run_hook(
        "guard_mcp_writes.py",
        {"tool_name": "github.get_file_contents", "tool_input": "{}"},
    )
    assert rc == 0
    assert _parse_stdout(out)["permission"] == "allow"


def test_guard_mcp_writes_denies_live_trading() -> None:
    rc, out, _err = _run_hook(
        "guard_mcp_writes.py",
        {"tool_name": "ccxt.create_order", "tool_input": "{}"},
    )
    assert rc == 0
    assert _parse_stdout(out)["permission"] == "deny"


def test_guard_mcp_writes_asks_for_github_writes() -> None:
    rc, out, _err = _run_hook(
        "guard_mcp_writes.py",
        {"tool_name": "github.create_pull_request", "tool_input": "{}"},
    )
    assert rc == 0
    assert _parse_stdout(out)["permission"] == "ask"


def test_guard_risk_files_logs_when_path_matches(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CURSOR_PROJECT_DIR", str(tmp_path))
    (tmp_path / ".cursor" / "state").mkdir(parents=True)

    body = json.dumps(
        {
            "hook_event_name": "afterFileEdit",
            "file_path": "/repo/risk/engine.py",
            "edits": [{"old_string": "a", "new_string": "b"}],
            "conversation_id": "c",
            "generation_id": "g",
        }
    )
    proc = subprocess.run(
        [PYTHON, str(HOOKS_DIR / "guard_risk_files.py")],
        input=body,
        text=True,
        capture_output=True,
        timeout=10,
        env={**os.environ, "CURSOR_PROJECT_DIR": str(tmp_path)},
        cwd=str(ROOT),
        check=False,
    )
    assert proc.returncode == 0
    log = (tmp_path / ".cursor" / "state" / "risk-touches.jsonl").read_text(encoding="utf-8")
    assert "risk/engine.py" in log


def test_guard_risk_files_ignores_unwatched_paths() -> None:
    rc, out, _err = _run_hook(
        "guard_risk_files.py",
        {
            "hook_event_name": "beforeReadFile",
            "file_path": "/repo/frontend/app/page.tsx",
            "content": "<html />",
        },
    )
    assert rc == 0
    assert _parse_stdout(out)["permission"] == "allow"


def test_format_python_no_op_on_non_python() -> None:
    rc, out, _err = _run_hook(
        "format_python.py",
        {"file_path": "/repo/README.md", "edits": [{"old_string": "a", "new_string": "b"}]},
    )
    assert rc == 0
    assert _parse_stdout(out) == {}


def test_append_session_log_writes_line(tmp_path) -> None:
    body = json.dumps({"text": "I did the thing."})
    proc = subprocess.run(
        [PYTHON, str(HOOKS_DIR / "append_session_log.py")],
        input=body,
        text=True,
        capture_output=True,
        timeout=10,
        env={**os.environ, "CURSOR_PROJECT_DIR": str(tmp_path)},
        cwd=str(ROOT),
        check=False,
    )
    assert proc.returncode == 0
    log = (tmp_path / "SESSION_LOG.md").read_text(encoding="utf-8")
    assert "[auto]" in log
    assert "I did the thing." in log


def test_record_thought_appends_jsonl(tmp_path) -> None:
    body = json.dumps(
        {"text": "thinking about the problem", "duration_ms": EXPECTED_DURATION_MS}
    )
    proc = subprocess.run(
        [PYTHON, str(HOOKS_DIR / "record_thought.py")],
        input=body,
        text=True,
        capture_output=True,
        timeout=10,
        env={**os.environ, "CURSOR_PROJECT_DIR": str(tmp_path)},
        cwd=str(ROOT),
        check=False,
    )
    assert proc.returncode == 0
    line = (tmp_path / ".cursor" / "state" / "thoughts.jsonl").read_text(encoding="utf-8")
    record = json.loads(line.strip())
    assert record["text"] == "thinking about the problem"
    assert record["duration_ms"] == EXPECTED_DURATION_MS


def test_record_thought_redacts_secrets(tmp_path) -> None:
    body = json.dumps({"text": 'config = {"api_key": "sk-abc123"}'})
    proc = subprocess.run(
        [PYTHON, str(HOOKS_DIR / "record_thought.py")],
        input=body,
        text=True,
        capture_output=True,
        timeout=10,
        env={**os.environ, "CURSOR_PROJECT_DIR": str(tmp_path)},
        cwd=str(ROOT),
        check=False,
    )
    assert proc.returncode == 0
    line = (tmp_path / ".cursor" / "state" / "thoughts.jsonl").read_text(encoding="utf-8")
    assert "sk-abc123" not in line
    assert "<redacted>" in line


def test_record_decisions_writes_pending(tmp_path) -> None:
    body = json.dumps({"status": "completed", "loop_count": 0, "conversation_id": "deadbeef"})
    proc = subprocess.run(
        [PYTHON, str(HOOKS_DIR / "record_decisions.py")],
        input=body,
        text=True,
        capture_output=True,
        timeout=10,
        env={**os.environ, "CURSOR_PROJECT_DIR": str(tmp_path)},
        cwd=str(ROOT),
        check=False,
    )
    assert proc.returncode == 0
    pending = (tmp_path / ".cursor" / "state" / "decisions-pending.md").read_text(encoding="utf-8")
    assert "deadbeef" in pending
    assert "completed" in pending


def test_pre_commit_review_allows_non_commit_command() -> None:
    rc, out, _err = _run_hook("pre_commit_review.py", {"command": "ls -la"})
    assert rc == 0
    assert _parse_stdout(out)["permission"] == "allow"
