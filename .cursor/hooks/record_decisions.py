"""stop hook: write a per-conversation summary that the reviewer agent reads.

We do NOT auto-edit DECISIONS.md. We append candidate notes to
``.cursor/state/decisions-pending.md`` for a human to ratify into
``DECISIONS.md`` (the audit trail).

``loop_limit`` is set to 1 in hooks.json so we never auto-resubmit.
"""

from __future__ import annotations

import contextlib
import json
import sys

from _common import (
    STATE_DIR,
    append_text,
    ensure_state,
    now_iso,
    read_input,
    write_output,
)

PENDING = STATE_DIR / "decisions-pending.md"
SUMMARY = STATE_DIR / "session-summary.json"


def main() -> None:
    payload = read_input()
    ensure_state()

    status = payload.get("status") or "unknown"
    loop_count = payload.get("loop_count")
    conversation_id = payload.get("conversation_id") or ""

    if not PENDING.exists():
        append_text(
            PENDING,
            "# Pending decisions\n\n"
            "Auto-generated session-stop notes. A human should compress these "
            "into `DECISIONS.md` and delete the entries that are now ratified.\n",
        )

    entry = (
        f"\n## {now_iso()} · conversation `{conversation_id[:12]}…`\n\n"
        f"- status: `{status}`\n"
        f"- loop_count: `{loop_count}`\n"
        f"- _Reviewer agent: scan this entry and propose any rule/skill changes "
        f"to `.cursor/state/proposed/`. Do NOT auto-edit `.cursor/rules/`._\n"
    )
    append_text(PENDING, entry)

    with contextlib.suppress(OSError):
        SUMMARY.write_text(
            json.dumps(
                {
                    "ts": now_iso(),
                    "conversation_id": conversation_id,
                    "status": status,
                    "loop_count": loop_count,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    write_output({})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"record_decisions hook error: {exc}\n")
        write_output({})
