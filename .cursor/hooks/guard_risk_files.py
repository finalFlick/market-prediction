"""beforeReadFile / afterFileEdit hook: log access to risk-critical files.

This hook does not block. It records access to `risk/`, `execution/`,
and `configs/risk.yaml` so the reviewer agent can spot unusual patterns.
"""

from __future__ import annotations

import sys

from _common import (
    STATE_DIR,
    allow,
    append_jsonl,
    ensure_state,
    now_iso,
    read_input,
    write_output,
)

WATCHED_PATH_FRAGMENTS = (
    "/risk/",
    "/execution/",
    "/configs/risk.yaml",
    "/configs/costs.yaml",
    "\\risk\\",
    "\\execution\\",
    "\\configs\\risk.yaml",
    "\\configs\\costs.yaml",
)


def is_watched(path: str) -> bool:
    if not path:
        return False
    p = path.replace("\\", "/").lower()
    return any(frag.replace("\\", "/").lower() in p for frag in WATCHED_PATH_FRAGMENTS)


def main() -> None:
    payload = read_input()
    ensure_state()

    event = payload.get("hook_event_name") or ""
    file_path = payload.get("file_path") or ""

    if not is_watched(file_path):
        if event == "beforeReadFile":
            allow()
        else:
            write_output({})
        return

    record = {
        "ts": now_iso(),
        "event": event,
        "file_path": file_path,
        "conversation_id": payload.get("conversation_id"),
        "generation_id": payload.get("generation_id"),
    }
    if event == "afterFileEdit":
        record["edits_n"] = len(payload.get("edits") or [])

    append_jsonl(STATE_DIR / "risk-touches.jsonl", record)

    if event == "beforeReadFile":
        allow()
    else:
        write_output({})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"guard_risk_files hook error: {exc}\n")
        write_output({})
