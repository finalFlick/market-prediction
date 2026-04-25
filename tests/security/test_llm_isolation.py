"""Enforce that the execution path cannot reach LLM code.

Per `.cursor/rules/llm-usage.mdc`: LLMs are research-only. No module under
`execution/` may transitively import `research.llm`. We verify this with
both static AST inspection and a runtime import check.
"""

from __future__ import annotations

import ast
import importlib
import pkgutil
import sys
from pathlib import Path

import pytest

import execution

_ROOT = Path(__file__).resolve().parents[2]
_FORBIDDEN_PREFIX = "research.llm"


def _walk_execution_modules() -> list[str]:
    return [
        m.name for m in pkgutil.walk_packages(execution.__path__, prefix=execution.__name__ + ".")
    ]


@pytest.mark.security
def test_execution_does_not_import_research_llm_at_runtime() -> None:
    """Drop research.llm from sys.modules then reload each execution.* module."""
    for mod_name in _walk_execution_modules():
        for k in [k for k in list(sys.modules) if k.startswith(_FORBIDDEN_PREFIX)]:
            del sys.modules[k]
        importlib.reload(importlib.import_module(mod_name))
        leaked = [m for m in sys.modules if m.startswith(_FORBIDDEN_PREFIX)]
        assert not leaked, f"{mod_name} transitively imported {leaked!r}"


@pytest.mark.security
def test_execution_source_does_not_reference_research_llm() -> None:
    """Belt-and-suspenders: AST scan all .py files under execution/."""
    offenders: list[str] = []
    for path in (_ROOT / "execution").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(_FORBIDDEN_PREFIX):
                        offenders.append(f"{path}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if mod.startswith(_FORBIDDEN_PREFIX):
                    offenders.append(f"{path}: from {mod} import …")
    assert not offenders, "LLM imports forbidden in execution/: " + "; ".join(offenders)
