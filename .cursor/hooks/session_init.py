"""sessionStart hook: inject orientation context for trading-lab agents.

Reads PROJECT_CONTEXT.md (truncated), the last 5 SESSION_LOG entries, and
any unreviewed proposals; returns them as ``additional_context`` so the
agent starts every conversation with the operating manual loaded.
"""

from __future__ import annotations

import sys
from pathlib import Path

from _common import (
    PROJECT_DIR,
    PROPOSED_DIR,
    ensure_state,
    read_input,
    write_output,
)

MAX_CONTEXT_CHARS = 8000
MAX_LOG_ENTRIES = 5
DOC_MAP_GLOBS: tuple[tuple[str, str], ...] = (
    ("docs", "*.md"),
    (".cursor/agents", "*.md"),
    (".cursor/skills", "*/SKILL.md"),
)


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


def _extract_title(path: Path) -> str:
    try:
        with path.open(encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line:
                    continue
                if line.startswith("# "):
                    return line[2:].strip()
                if line.startswith("---"):
                    continue
                return line
    except OSError:
        pass
    return path.stem


def build_doc_map() -> str:
    entries: list[str] = []
    for rel_dir, pattern in DOC_MAP_GLOBS:
        base = PROJECT_DIR / rel_dir
        if not base.exists():
            continue
        for path in sorted(base.glob(pattern)):
            try:
                rel = path.relative_to(PROJECT_DIR).as_posix()
            except ValueError:
                continue
            title = _extract_title(path)
            entries.append(f"- `{rel}` — {title}")
    if not entries:
        return ""
    header = (
        "## Steering files (read on demand)\n"
        "These files are NOT auto-loaded; read them when relevant.\n"
    )
    return header + "\n".join(entries)


def how_to_invoke() -> str:
    return (
        "## How to invoke\n"
        "- For multi-file tasks, run the `session-init` skill at "
        "`.cursor/skills/session-init/SKILL.md` to load PROJECT_CONTEXT, "
        "AGENTS, and the matching rule MDC into your working memory."
    )


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

    doc_map = build_doc_map()
    if doc_map:
        parts.append("\n" + doc_map)

    parts.append("\n" + how_to_invoke())

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
