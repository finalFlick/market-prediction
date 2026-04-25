"""Filesystem helpers for the prompt-context-router hooks.

Atomic JSON writes, tolerant JSON reads, JSONL append-and-truncate.
All helpers swallow ``OSError`` paths and return safe defaults so the
hooks remain fail-open.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def atomic_write_json(path: Path, obj: Any) -> bool:
    """Write ``obj`` to ``path`` atomically. Returns True on success."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        text = json.dumps(obj, ensure_ascii=False)
        with tmp.open("w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except OSError:
        return False
    return True


def read_json(path: Path) -> Any:
    """Read JSON from ``path``. Returns ``None`` on any failure."""
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def append_jsonl(path: Path, record: dict[str, Any]) -> bool:
    """Append a single JSON record to ``path`` as a new line.

    Returns True on success, False on any OSError. Errors are swallowed
    to keep the caller fail-open.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(record, ensure_ascii=False) + "\n"
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except OSError:
        return False
    return True


def truncate_jsonl(path: Path, max_lines: int) -> bool:
    """Keep only the last ``max_lines`` of ``path``.

    Reads the whole file, slices the tail, rewrites atomically. The
    cost is acceptable because the cap is small (5000 lines) and this
    runs once per hook invocation.
    """
    if max_lines <= 0:
        return False
    try:
        if not path.exists():
            return True
        with path.open(encoding="utf-8") as fh:
            lines = fh.readlines()
        if len(lines) <= max_lines:
            return True
        tail = lines[-max_lines:]
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            fh.writelines(tail)
        os.replace(tmp, path)
    except OSError:
        return False
    return True
