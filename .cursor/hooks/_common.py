"""Shared utilities for Cursor hook scripts.

Hooks must be robust: they read JSON from stdin, write JSON (or nothing)
to stdout, and never raise. A crashing hook with ``failClosed: true``
blocks the agent action; without it, it fails open. Either way, a clean
exit with a useful response is the goal.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_DIR = Path(os.environ.get("CURSOR_PROJECT_DIR", os.getcwd())).resolve()
STATE_DIR = PROJECT_DIR / ".cursor" / "state"
PROPOSED_DIR = STATE_DIR / "proposed"

SECRET_KEYS = {
    "api_key",
    "api_secret",
    "secret",
    "password",
    "passphrase",
    "signature",
    "token",
    "authorization",
    "private_key",
}


def read_input() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def write_output(payload: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(payload))
    sys.stdout.flush()


def allow() -> None:
    write_output({"permission": "allow"})


def deny(user_message: str, agent_message: str | None = None) -> None:
    body: dict[str, Any] = {
        "permission": "deny",
        "user_message": user_message,
    }
    if agent_message:
        body["agent_message"] = agent_message
    write_output(body)


def ask(user_message: str, agent_message: str | None = None) -> None:
    body: dict[str, Any] = {
        "permission": "ask",
        "user_message": user_message,
    }
    if agent_message:
        body["agent_message"] = agent_message
    write_output(body)


def ensure_state() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    PROPOSED_DIR.mkdir(parents=True, exist_ok=True)


def now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def redact(text: str) -> str:
    """Remove obvious secret-like values from a string."""
    out = text
    for key in SECRET_KEYS:
        for needle in (f'"{key}"', f"'{key}'", f"{key}="):
            i = out.lower().find(needle.lower())
            if i == -1:
                continue
            j = out.find("\n", i)
            if j == -1:
                j = len(out)
            out = out[:i] + f"{needle}=<redacted>" + out[j:]
    return out


def append_text(path: Path, text: str) -> None:
    """Append text to a file, creating parents as needed. Robust to errors."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(text)
    except OSError:
        pass


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        pass
