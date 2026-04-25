"""afterAgentThought hook: record reasoning blocks for later review.

Writes redacted thinking to ``.cursor/state/thoughts.jsonl``. The
``reviewer`` agent reads this file when looking for patterns that justify
new rules or skills. Humans can also `tail -f` it during a session.
"""

from __future__ import annotations

import sys

from _common import (
    STATE_DIR,
    append_jsonl,
    ensure_state,
    now_iso,
    read_input,
    redact,
    write_output,
)


def main() -> None:
    payload = read_input()
    text = payload.get("text") or ""
    if not text.strip():
        write_output({})
        return

    ensure_state()
    record = {
        "ts": now_iso(),
        "conversation_id": payload.get("conversation_id"),
        "generation_id": payload.get("generation_id"),
        "duration_ms": payload.get("duration_ms"),
        "text": redact(text)[:4000],
    }
    append_jsonl(STATE_DIR / "thoughts.jsonl", record)
    write_output({})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"record_thought hook error: {exc}\n")
        write_output({})
