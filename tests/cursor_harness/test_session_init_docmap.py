"""Tests for the augmented ``session_init.py`` doc map."""

from __future__ import annotations

import importlib
import io
import json
import sys
from pathlib import Path

import pytest


def _run(monkeypatch: pytest.MonkeyPatch) -> dict:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"session_id": "X"})))
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    if "session_init" in sys.modules:
        del sys.modules["session_init"]
    mod = importlib.import_module("session_init")
    mod.main()
    return json.loads(out.getvalue())


def test_session_init_includes_doc_map(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (project_dir / "PROJECT_CONTEXT.md").write_text(
        "# PROJECT_CONTEXT\nentry doc body", encoding="utf-8"
    )
    (project_dir / "SESSION_LOG.md").write_text(
        "# Session Log\n\n## 2026-04-25 — sample\n- a\n", encoding="utf-8"
    )
    docs = project_dir / "docs"
    docs.mkdir()
    (docs / "RISK_POLICY.md").write_text("# Risk Policy\nbody", encoding="utf-8")
    (docs / "DATA_MODEL.md").write_text("# Data Model\nbody", encoding="utf-8")

    agents = project_dir / ".cursor" / "agents"
    agents.mkdir(parents=True)
    (agents / "research.md").write_text("# ResearchAgent\nrole", encoding="utf-8")

    skills = project_dir / ".cursor" / "skills" / "session-init"
    skills.mkdir(parents=True)
    (skills / "SKILL.md").write_text("# session-init\nrole", encoding="utf-8")

    payload = _run(monkeypatch)
    text = payload["additional_context"]

    assert "## Steering files (read on demand)" in text
    assert "docs/RISK_POLICY.md" in text
    assert "docs/DATA_MODEL.md" in text
    assert ".cursor/agents/research.md" in text
    assert ".cursor/skills/session-init/SKILL.md" in text
    assert "## How to invoke" in text
    assert "session-init" in text


def test_session_init_respects_budget(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (project_dir / "PROJECT_CONTEXT.md").write_text("Z" * 50000, encoding="utf-8")
    payload = _run(monkeypatch)
    assert len(payload["additional_context"]) <= 8000
