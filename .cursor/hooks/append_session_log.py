"""afterAgentResponse hook: append a one-line summary to SESSION_LOG.md.

We only summarize the response (first 200 chars); we do not echo the
full transcript. SESSION_LOG.md is human-curated; this hook adds
machine-noted entries that humans can compress later.
"""

from __future__ import annotations

import sys

from _common import (
    PROJECT_DIR,
    append_text,
    now_iso,
    read_input,
    redact,
    write_output,
)

LOG_PATH = PROJECT_DIR / "SESSION_LOG.md"
HEADER = "# Session log\n\nAuto-noted lines start with `[auto]`. Compress periodically.\n"


def first_line(text: str, n: int = 200) -> str:
    if not text:
        return ""
    cleaned = " ".join(text.split())
    if len(cleaned) > n:
        cleaned = cleaned[: n - 1] + "…"
    return cleaned


def main() -> None:
    payload = read_input()
    text = payload.get("text") or ""
    if not text.strip():
        write_output({})
        return

    if not LOG_PATH.exists():
        append_text(LOG_PATH, HEADER)

    line = f"\n- [auto] {now_iso()} · {redact(first_line(text))}\n"
    append_text(LOG_PATH, line)
    write_output({})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"append_session_log hook error: {exc}\n")
        write_output({})
