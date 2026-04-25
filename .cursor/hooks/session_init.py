"""sessionStart hook: inject orientation context for trading-lab agents.

Reads PROJECT_CONTEXT.md (truncated), the last 5 SESSION_LOG entries, and
any unreviewed proposals; returns them as ``additional_context`` so the
agent starts every conversation with the operating manual loaded.
"""

from __future__ import annotations

import sys

from _common import (
    PROJECT_DIR,
    PROPOSED_DIR,
    ensure_state,
    read_input,
    write_output,
)

MAX_CONTEXT_CHARS = 6000
MAX_LOG_ENTRIES = 5


def safe_read(path, max_chars: int) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 80] + "\n\n... [truncated to fit context budget] ..."


def tail_log_entries(path, n: int) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    parts = [p for p in text.split("\n## ") if p.strip()]
    if not parts:
        return text[-2000:]
    tail = parts[-n:]
    return "\n## " + "\n## ".join(tail)


def list_proposals() -> str:
    if not PROPOSED_DIR.exists():
        return ""
    files = sorted(PROPOSED_DIR.glob("*.md"))
    if not files:
        return ""
    lines = ["Pending self-improvement proposals (`.cursor/state/proposed/`):"]
    for f in files[:5]:
        lines.append(f"- {f.name}")
    return "\n".join(lines)


def main() -> None:
    read_input()
    ensure_state()

    parts = ["# trading-lab session orientation\n"]

    project_context = safe_read(PROJECT_DIR / "PROJECT_CONTEXT.md", 2500)
    if project_context:
        parts.append("## PROJECT_CONTEXT.md (entry doc)\n")
        parts.append(project_context)

    log_tail = tail_log_entries(PROJECT_DIR / "SESSION_LOG.md", MAX_LOG_ENTRIES)
    if log_tail:
        parts.append("\n## Recent SESSION_LOG entries\n")
        parts.append(log_tail)

    proposals = list_proposals()
    if proposals:
        parts.append("\n## Pending proposals (review, do not auto-apply)\n")
        parts.append(proposals)

    parts.append(
        "\n## Reminders\n"
        "- Risk is non-bypassable; every order goes through `risk.engine`.\n"
        "- LLMs are research-only; `execution/` cannot import `research.llm`.\n"
        "- Plan-first for any multi-file change. Run tests before declaring done."
    )

    additional_context = "\n".join(parts)
    if len(additional_context) > MAX_CONTEXT_CHARS:
        additional_context = additional_context[: MAX_CONTEXT_CHARS - 80] + "\n\n... [truncated]"

    write_output({"additional_context": additional_context})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"session_init hook error: {exc}\n")
        write_output({})
