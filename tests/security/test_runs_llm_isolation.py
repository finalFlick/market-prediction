"""``runs/`` must not import ``research.llm`` (Invariant 2)."""

from __future__ import annotations

import ast
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_RUNS = _ROOT / "runs"
_FORBIDDEN = "research.llm"


def test_runs_tree_never_imports_llm() -> None:
    if not _RUNS.is_dir():
        return
    bad: list[str] = []
    for path in _RUNS.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(_FORBIDDEN):
                        bad.append(f"{path}: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                m = node.module or ""
                if m.startswith(_FORBIDDEN):
                    bad.append(f"{path}: from {m}")
    assert not bad, bad
