"""beforeSubmitPrompt hook: persist the user's prompt for downstream routing.

Companion to ``prompt_context_router.py`` (postToolUse). The Cursor
hook contract for ``beforeSubmitPrompt`` does not allow injecting
``additional_context``, so this hook only writes the prompt to a
known location and returns ``{"continue": true}``. The
``postToolUse`` router reads the file as one of its routing signals.

Fail-open by construction: any exception is logged to stderr; the
hook always emits ``{"continue": true}`` and exits 0.
"""

from __future__ import annotations

import contextlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from _common import PROJECT_DIR, ensure_state, read_input, redact, write_output
from _router_io import atomic_write_json
from _router_types import LastPromptRecord

LAST_PROMPT_PATH = PROJECT_DIR / ".cursor" / "state" / "last-prompt.json"
MAX_PROMPT_CHARS = 8000


def _disabled() -> bool:
    val = os.environ.get("TLAB_ROUTER_DISABLE", "").strip().lower()
    return val not in ("", "0", "false", "no")


def _build_record(payload: dict[str, Any]) -> LastPromptRecord:
    raw_prompt = payload.get("prompt")
    prompt = raw_prompt if isinstance(raw_prompt, str) else ""
    prompt = redact(prompt)
    if len(prompt) > MAX_PROMPT_CHARS:
        prompt = prompt[:MAX_PROMPT_CHARS]

    attachments_raw = payload.get("attachments")
    attachments: list[dict[str, object]] = []
    if isinstance(attachments_raw, list):
        for item in attachments_raw:
            if isinstance(item, dict):
                attachments.append({str(k): v for k, v in item.items()})

    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        session_id = "unknown"

    return {
        "session_id": session_id,
        "prompt": prompt,
        "attachments": attachments,
        "captured_at": datetime.now(tz=timezone.utc).isoformat(),
    }


def main() -> None:
    payload = read_input()
    if _disabled():
        write_output({"continue": True})
        return

    ensure_state()
    LAST_PROMPT_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = _build_record(payload)
    ok = atomic_write_json(Path(LAST_PROMPT_PATH), record)
    if not ok:
        sys.stderr.write("[router] prompt_capture: failed to write last-prompt.json\n")

    write_output({"continue": True})


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        sys.stderr.write(f"[router] prompt_capture crashed: {exc!r}\n")
        with contextlib.suppress(BaseException):
            write_output({"continue": True})
