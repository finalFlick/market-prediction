"""Shared fixtures for ``tests/cursor_harness/`` router tests.

The hooks live under ``.cursor/hooks/`` which is not on ``sys.path``
by default (and shouldn't be — they're not a package). Tests that
import the hook modules add the hooks directory to ``sys.path``
through the ``hooks_path`` fixture below.
"""

from __future__ import annotations

import contextlib
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = ROOT / ".cursor" / "hooks"


_HOOK_MODULE_PREFIXES = (
    "_common",
    "_router_",
    "prompt_capture",
    "prompt_context_router",
    "session_init",
)


def _purge_hook_modules() -> None:
    for mod in list(sys.modules):
        if mod.startswith(_HOOK_MODULE_PREFIXES):
            del sys.modules[mod]


@pytest.fixture(autouse=True)
def hooks_path() -> Iterator[None]:
    """Make ``.cursor/hooks/`` importable for the duration of the test.

    Also purges any cached hook modules before and after each test so
    ``_common.PROJECT_DIR`` (computed at import time from
    ``CURSOR_PROJECT_DIR``) reflects the current test's tmp directory.
    """
    p = str(HOOKS_DIR)
    added = p not in sys.path
    if added:
        sys.path.insert(0, p)
    _purge_hook_modules()
    try:
        yield
    finally:
        if added:
            with contextlib.suppress(ValueError):
                sys.path.remove(p)
        _purge_hook_modules()


@pytest.fixture
def project_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a tmp project root with ``.cursor/state/`` ready for hooks."""
    state = tmp_path / ".cursor" / "state"
    state.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("CURSOR_PROJECT_DIR", str(tmp_path))
    monkeypatch.delenv("TLAB_ROUTER_DISABLE", raising=False)
    monkeypatch.delenv("TLAB_ROUTER_BUDGET_CHARS", raising=False)
    return tmp_path
