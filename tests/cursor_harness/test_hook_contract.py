"""Subprocess contract tests for the new hooks.

Cursor invokes hooks as subprocesses. We replicate that here for the
two new scripts to confirm the IPC contract holds end to end.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / ".cursor" / "hooks"


def _run(
    script: str,
    payload: dict,
    *,
    env_extra: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    env = {**os.environ, "CURSOR_PROJECT_DIR": str(ROOT)}
    if env_extra:
        env.update(env_extra)
    proc = subprocess.run(
        [sys.executable, str(HOOKS / script)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        timeout=15,
        env=env,
        cwd=str(ROOT),
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def test_prompt_capture_subprocess_returns_continue_true() -> None:
    rc, out, _err = _run(
        "prompt_capture.py",
        {"session_id": "ci", "prompt": "do it", "attachments": []},
        env_extra={"TLAB_ROUTER_DISABLE": "1"},
    )
    assert rc == 0
    assert json.loads(out.strip()) == {"continue": True}


def test_prompt_capture_subprocess_handles_empty_stdin() -> None:
    proc = subprocess.run(
        [sys.executable, str(HOOKS / "prompt_capture.py")],
        input="",
        text=True,
        capture_output=True,
        timeout=15,
        env={**os.environ, "CURSOR_PROJECT_DIR": str(ROOT), "TLAB_ROUTER_DISABLE": "1"},
        cwd=str(ROOT),
        check=False,
    )
    assert proc.returncode == 0


def test_router_subprocess_returns_object_when_disabled() -> None:
    rc, out, _err = _run(
        "prompt_context_router.py",
        {"tool_name": "Read", "tool_input": {"path": "AGENTS.md"}, "tool_output": ""},
        env_extra={"TLAB_ROUTER_DISABLE": "1"},
    )
    assert rc == 0
    assert json.loads(out.strip()) == {}


def test_router_subprocess_handles_malformed_stdin() -> None:
    proc = subprocess.run(
        [sys.executable, str(HOOKS / "prompt_context_router.py")],
        input="this is not json",
        text=True,
        capture_output=True,
        timeout=15,
        env={**os.environ, "CURSOR_PROJECT_DIR": str(ROOT), "TLAB_ROUTER_DISABLE": "1"},
        cwd=str(ROOT),
        check=False,
    )
    assert proc.returncode == 0
