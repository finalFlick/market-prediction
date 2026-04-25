"""Tests for the dependency-research hook and its hooks.json wiring.

Covers three layers:

1. The script's ``--self-test`` mode passes (regex/parsing correctness).
2. Subprocess invocation honors the Cursor IPC contract for both the
   ``beforeShellExecution`` and ``afterFileEdit`` events.
3. ``.cursor/hooks.json`` registers the hook on both events without a
   restrictive matcher (so it actually fires).
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
HOOK_SCRIPT = HOOKS_DIR / "check_dependency_research.py"
HOOKS_JSON = ROOT / ".cursor" / "hooks.json"


def _run_hook(
    payload: dict,
    *,
    cwd: Path | None = None,
    env_extra: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    env = {**os.environ, "CURSOR_PROJECT_DIR": str(cwd or ROOT)}
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=15,
        env=env,
        cwd=str(cwd or ROOT),
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _parse(stdout: str) -> dict:
    s = stdout.strip()
    return json.loads(s) if s else {}


# --- self-test --------------------------------------------------------------


def test_self_test_passes() -> None:
    proc = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT), "--self-test"],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "PASSED" in proc.stdout
    assert "FAILED" not in proc.stdout


# --- beforeShellExecution ---------------------------------------------------


@pytest.mark.parametrize(
    ("command", "expected_pkg_substr"),
    [
        ("pip install requests", "requests"),
        ("pip3 install httpx tenacity", "httpx"),
        ("python -m pip install --upgrade pandas", "pandas"),
        ("uv add ruff", "ruff"),
        ("uv pip install mypy==1.10.0", "mypy"),
        ("poetry add lightgbm", "lightgbm"),
        ("npm install react", "react"),
        ("npm i lodash", "lodash"),
        ("yarn add @tanstack/react-query", "tanstack"),
        ("pnpm add zod", "zod"),
        ("conda install -c conda-forge polars", "polars"),
    ],
)
def test_install_commands_ask_for_permission(command: str, expected_pkg_substr: str) -> None:
    rc, out, _err = _run_hook({"hook_event_name": "beforeShellExecution", "command": command})
    assert rc == 0
    body = _parse(out)
    assert body["permission"] == "ask"
    assert "user_message" in body
    assert "agent_message" in body
    assert "library-research" in body["agent_message"]
    assert expected_pkg_substr in body["agent_message"]


@pytest.mark.parametrize(
    "command",
    [
        "pip install -e .",
        "pip install -r requirements.txt",
        "npm install",
        "yarn install",
        "pip --version",
        "ruff check .",
        "git status",
        "python -m pytest -q",
        "python scripts/install.py",
        "echo 'pip install foo'",
    ],
)
def test_non_install_commands_allow(command: str) -> None:
    rc, out, _err = _run_hook({"hook_event_name": "beforeShellExecution", "command": command})
    assert rc == 0
    assert _parse(out)["permission"] == "allow"


def test_empty_command_allows() -> None:
    rc, out, _err = _run_hook({"hook_event_name": "beforeShellExecution"})
    assert rc == 0
    assert _parse(out)["permission"] == "allow"


def test_handles_malformed_stdin() -> None:
    proc = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input="this is not json",
        text=True,
        capture_output=True,
        timeout=10,
        env={**os.environ, "CURSOR_PROJECT_DIR": str(ROOT)},
        cwd=str(ROOT),
        check=False,
    )
    assert proc.returncode == 0


# --- afterFileEdit ----------------------------------------------------------


def test_manifest_edit_with_new_dep_emits_message_and_logs(tmp_path: Path) -> None:
    payload = {
        "hook_event_name": "afterFileEdit",
        "file_path": "/repo/pyproject.toml",
        "edits": [
            {
                "old_string": '"pandas>=2.0",\n',
                "new_string": '"pandas>=2.0",\n"requests==2.32.0",\n',
            }
        ],
        "conversation_id": "conv-1",
        "generation_id": "gen-1",
    }
    rc, out, _err = _run_hook(payload, cwd=tmp_path)
    assert rc == 0
    body = _parse(out)
    assert "agent_message" in body
    assert "library-research" in body["agent_message"]
    assert "requests==2.32.0" in body["agent_message"]

    log = tmp_path / ".cursor" / "state" / "dependency-touches.jsonl"
    assert log.exists()
    record = json.loads(log.read_text(encoding="utf-8").strip())
    assert record["file_path"] == "/repo/pyproject.toml"
    assert any("requests==2.32.0" in line for line in record["added_lines"])


def test_package_json_new_dep_is_flagged(tmp_path: Path) -> None:
    payload = {
        "hook_event_name": "afterFileEdit",
        "file_path": "/repo/frontend/package.json",
        "edits": [
            {
                "old_string": '    "next": "14.2.0"\n',
                "new_string": '    "next": "14.2.0",\n    "zod": "^3.23.0"\n',
            }
        ],
    }
    rc, out, _err = _run_hook(payload, cwd=tmp_path)
    assert rc == 0
    body = _parse(out)
    assert "zod" in body.get("agent_message", "")


def test_non_manifest_edit_is_silent(tmp_path: Path) -> None:
    payload = {
        "hook_event_name": "afterFileEdit",
        "file_path": "/repo/README.md",
        "edits": [{"old_string": "x", "new_string": '"foo": "1.0"'}],
    }
    rc, out, _err = _run_hook(payload, cwd=tmp_path)
    assert rc == 0
    assert _parse(out) == {}


def test_manifest_edit_without_new_dep_is_silent(tmp_path: Path) -> None:
    payload = {
        "hook_event_name": "afterFileEdit",
        "file_path": "/repo/pyproject.toml",
        "edits": [
            {
                "old_string": "name = 'old'",
                "new_string": "name = 'old'\n# just a comment",
            }
        ],
    }
    rc, out, _err = _run_hook(payload, cwd=tmp_path)
    assert rc == 0
    assert _parse(out) == {}


# --- hooks.json wiring ------------------------------------------------------


def _hooks() -> dict:
    return json.loads(HOOKS_JSON.read_text(encoding="utf-8"))


def test_hooks_json_registers_dependency_research_on_shell() -> None:
    entries = _hooks()["hooks"].get("beforeShellExecution", [])
    matching = [e for e in entries if "check_dependency_research.py" in e["command"]]
    assert len(matching) == 1
    # Must NOT be failClosed: the hook is advisory, not authoritative.
    assert matching[0].get("failClosed") is not True
    # Must NOT have a narrow matcher; the hook needs to see all commands.
    assert "matcher" not in matching[0]


def test_hooks_json_registers_dependency_research_on_edit() -> None:
    entries = _hooks()["hooks"].get("afterFileEdit", [])
    matching = [e for e in entries if "check_dependency_research.py" in e["command"]]
    assert len(matching) == 1
    assert matching[0].get("failClosed") is not True
    assert "matcher" not in matching[0]


def test_existing_shell_hooks_still_present() -> None:
    """Sanity: we registered the new hook without removing the old ones."""
    serialized = json.dumps(_hooks()["hooks"]["beforeShellExecution"])
    assert "block_dangerous_shell.py" in serialized
    assert "no_inline_python.py" in serialized
    assert "pre_commit_review.py" in serialized
