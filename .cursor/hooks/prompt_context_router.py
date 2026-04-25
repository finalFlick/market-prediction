"""postToolUse hook: inject relevant steering-file snippets after tool calls.

Reads:

- ``.cursor/state/last-prompt.json`` (written by ``prompt_capture.py``)
- ``.cursor/context-router.json`` (committed routing table)
- ``.cursor/state/session-context-memory.json`` (per-session dedupe)

Emits ``{"additional_context": "..."}`` on stdout when at least one
routing rule fires; otherwise emits ``{}``. Always exits 0; any
unhandled exception is caught at the top level so a buggy router
never blocks the agent.
"""

from __future__ import annotations

import contextlib
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, cast

from _common import PROJECT_DIR, ensure_state, read_input, write_output
from _router_core import (
    empty_log_record,
    empty_memory,
    load_routing_table,
    route,
)
from _router_io import append_jsonl, atomic_write_json, read_json, truncate_jsonl
from _router_types import LastPromptRecord, SessionMemoryFile

ROUTING_TABLE_PATH = PROJECT_DIR / ".cursor" / "context-router.json"
LAST_PROMPT_PATH = PROJECT_DIR / ".cursor" / "state" / "last-prompt.json"
SESSION_MEMORY_PATH = PROJECT_DIR / ".cursor" / "state" / "session-context-memory.json"
ROUTER_LOG_PATH = PROJECT_DIR / ".cursor" / "state" / "router-log.jsonl"

DEFAULT_BUDGET_CHARS = 3000
PROMPT_FRESHNESS_MIN = 30
LOG_MAX_LINES = 5000


def _disabled() -> bool:
    val = os.environ.get("TLAB_ROUTER_DISABLE", "").strip().lower()
    return val not in ("", "0", "false", "no")


def _budget() -> int:
    raw = os.environ.get("TLAB_ROUTER_BUDGET_CHARS")
    if raw is None or not raw.strip():
        return DEFAULT_BUDGET_CHARS
    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_BUDGET_CHARS
    return max(0, value)


def _load_last_prompt(now: datetime) -> LastPromptRecord | None:
    raw = read_json(LAST_PROMPT_PATH)
    if not isinstance(raw, dict):
        return None
    captured_at = raw.get("captured_at")
    ts: datetime | None = None
    if isinstance(captured_at, str):
        try:
            ts = datetime.fromisoformat(captured_at)
        except ValueError:
            ts = None
    if ts is not None and ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    if ts is None:
        try:
            mtime = LAST_PROMPT_PATH.stat().st_mtime
            ts = datetime.fromtimestamp(mtime, tz=timezone.utc)
        except OSError:
            return None
    if now - ts > timedelta(minutes=PROMPT_FRESHNESS_MIN):
        return None
    prompt = raw.get("prompt")
    session_id = raw.get("session_id")
    attachments_raw = raw.get("attachments")
    record: LastPromptRecord = {
        "session_id": session_id if isinstance(session_id, str) else "unknown",
        "prompt": prompt if isinstance(prompt, str) else "",
        "attachments": list(attachments_raw) if isinstance(attachments_raw, list) else [],
        "captured_at": ts.isoformat(),
    }
    return record


def _load_memory() -> SessionMemoryFile:
    raw = read_json(SESSION_MEMORY_PATH)
    if not isinstance(raw, dict):
        return empty_memory()
    sessions_raw = raw.get("sessions")
    if not isinstance(sessions_raw, dict):
        return empty_memory()
    return cast(SessionMemoryFile, {"version": 1, "sessions": sessions_raw})


def main() -> None:
    payload: dict[str, Any] = read_input()
    if _disabled():
        write_output({})
        return

    ensure_state()
    now = datetime.now(tz=timezone.utc)
    table = load_routing_table(ROUTING_TABLE_PATH)
    if table is None:
        write_output({})
        return

    last_prompt = _load_last_prompt(now)
    memory = _load_memory()
    budget = _budget()

    text, updated_memory, log_record = route(
        hook_input=payload,
        last_prompt=last_prompt,
        routing_table=table,
        session_memory=memory,
        budget_chars=budget,
        project_dir=PROJECT_DIR,
        now=now,
    )

    if log_record["matched_rule_ids"] or log_record["injected_snippets"]:
        append_jsonl(ROUTER_LOG_PATH, dict(log_record))
        truncate_jsonl(ROUTER_LOG_PATH, LOG_MAX_LINES)

    if log_record["injected_snippets"]:
        atomic_write_json(SESSION_MEMORY_PATH, updated_memory)

    if text:
        write_output({"additional_context": text})
    else:
        write_output({})


def _safe_log(record: dict[str, Any]) -> None:
    with contextlib.suppress(BaseException):
        append_jsonl(ROUTER_LOG_PATH, record)


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        sys.stderr.write(f"[router] prompt_context_router crashed: {exc!r}\n")
        _safe_log(
            dict(
                empty_log_record(
                    session_id="unknown",
                    tool_name="<crash>",
                    now=datetime.now(tz=timezone.utc),
                )
            )
            | {"skip_reason": f"exception: {type(exc).__name__}"}
        )
        with contextlib.suppress(BaseException):
            write_output({})
