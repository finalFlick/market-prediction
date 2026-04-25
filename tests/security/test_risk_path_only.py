"""Strategies must not import execution (Req 20, 24) — all orders flow through risk."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STRATEGIES = ROOT / "strategies"


def _imports_execution_brokers(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("execution.brokers"):
                    return True
        elif isinstance(node, ast.ImportFrom) and (
            node.module and node.module.startswith("execution.brokers")
        ):
            return True
    return False


def test_strategies_never_import_execution_brokers() -> None:
    py_files = [p for p in STRATEGIES.rglob("*.py") if p.is_file() and p.name != "__pycache__"]
    assert py_files, "expected strategy modules"
    bad = [p for p in py_files if _imports_execution_brokers(p)]
    assert not bad, f"strategies/ must not import execution.brokers: {bad}"
