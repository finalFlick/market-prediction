"""End-to-end smoke: three turns, three rules fire, capture → router."""

from __future__ import annotations

import importlib
import io
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _seed_steering_files(project_dir: Path) -> None:
    """Mirror the few steering files the smoke turns will route to."""
    (project_dir / "AGENTS.md").write_text("# AGENTS\nbody", encoding="utf-8")
    (project_dir / "SIGNALS.md").write_text("# SIGNALS\nlist of signals", encoding="utf-8")
    docs = project_dir / "docs"
    docs.mkdir()
    (docs / "RISK_POLICY.md").write_text("# Risk Policy\nrules and limits", encoding="utf-8")
    (docs / "EVALUATION.md").write_text("# Evaluation\nwalk-forward", encoding="utf-8")
    (docs / "DATA_MODEL.md").write_text("# Data Model\nDuckDB layout", encoding="utf-8")
    rules = project_dir / ".cursor" / "rules"
    rules.mkdir(parents=True, exist_ok=True)
    (rules / "risk-management.mdc").write_text("# risk rules\nbody", encoding="utf-8")
    (rules / "backtesting.mdc").write_text("# backtest rules\nbody", encoding="utf-8")
    (rules / "research-workflow.mdc").write_text("# research\nbody", encoding="utf-8")
    agents = project_dir / ".cursor" / "agents"
    agents.mkdir(parents=True, exist_ok=True)
    (agents / "signal.md").write_text("# SignalAgent\nrole", encoding="utf-8")
    (agents / "research.md").write_text("# ResearchAgent\nrole", encoding="utf-8")


def _copy_routing_table(project_dir: Path) -> None:
    real = ROOT / ".cursor" / "context-router.json"
    target = project_dir / ".cursor" / "context-router.json"
    target.write_text(real.read_text(encoding="utf-8"), encoding="utf-8")


def _run_capture(payload: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    monkeypatch.setattr(sys, "stdout", io.StringIO())
    monkeypatch.setattr(sys, "stderr", io.StringIO())
    if "prompt_capture" in sys.modules:
        del sys.modules["prompt_capture"]
    importlib.import_module("prompt_capture").main()


def _run_router(payload: dict, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", io.StringIO())
    if "prompt_context_router" in sys.modules:
        del sys.modules["prompt_context_router"]
    importlib.import_module("prompt_context_router").main()
    return json.loads(out.getvalue())


def test_smoke_three_turns_three_rules(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _seed_steering_files(project_dir)
    _copy_routing_table(project_dir)

    fired: set[str] = set()

    _run_capture({"session_id": "smoke", "prompt": "fix the kill switch in risk"}, monkeypatch)
    out = _run_router(
        {
            "tool_name": "Read",
            "tool_input": {"path": "risk/engine.py"},
            "tool_output": "",
            "agent_message": "Looking at risk engine",
        },
        monkeypatch,
    )
    if "additional_context" in out:
        fired.add("risk-policy" if "RISK_POLICY" in out["additional_context"] else "?")

    _run_capture(
        {"session_id": "smoke", "prompt": "rerun the backtest with embargo"},
        monkeypatch,
    )
    out = _run_router(
        {
            "tool_name": "Grep",
            "tool_input": {"pattern": "embargo", "path": "backtests/"},
            "tool_output": "",
            "agent_message": "Searching for embargo logic",
        },
        monkeypatch,
    )
    if "additional_context" in out:
        fired.add("evaluation-gates" if "EVALUATION" in out["additional_context"] else "?")

    _run_capture(
        {"session_id": "smoke", "prompt": "add a binance ohlcv ingest"},
        monkeypatch,
    )
    out = _run_router(
        {
            "tool_name": "Read",
            "tool_input": {"path": "data/ingest/binance.py"},
            "tool_output": "",
            "agent_message": "Inspecting the binance ingest",
        },
        monkeypatch,
    )
    if "additional_context" in out:
        fired.add("data-ingest" if "DATA_MODEL" in out["additional_context"] else "?")

    assert len(fired) >= 3, f"only fired: {fired}"

    log = (project_dir / ".cursor" / "state" / "router-log.jsonl").read_text(encoding="utf-8")
    assert log.strip(), "router-log.jsonl should have entries"
    for line in log.strip().splitlines():
        record = json.loads(line)
        assert "fix the kill switch" not in json.dumps(record)
