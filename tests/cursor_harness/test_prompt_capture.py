"""Tests for ``.cursor/hooks/prompt_capture.py``."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest


def _run_main(payload: dict, monkeypatch: pytest.MonkeyPatch) -> tuple[str, str]:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    out = io.StringIO()
    err = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    monkeypatch.setattr(sys, "stderr", err)

    import importlib

    if "prompt_capture" in sys.modules:
        del sys.modules["prompt_capture"]
    mod = importlib.import_module("prompt_capture")
    mod.main()
    return out.getvalue(), err.getvalue()


def test_capture_writes_record(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out, _err = _run_main(
        {"session_id": "S1", "prompt": "fix the kill switch", "attachments": []},
        monkeypatch,
    )
    assert json.loads(out) == {"continue": True}

    record = json.loads(
        (project_dir / ".cursor" / "state" / "last-prompt.json").read_text(encoding="utf-8")
    )
    assert record["session_id"] == "S1"
    assert record["prompt"] == "fix the kill switch"
    assert record["captured_at"]


def test_capture_redacts_secrets(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _run_main(
        {"session_id": "S2", "prompt": 'set api_key="sk-LIVE" and proceed'},
        monkeypatch,
    )
    record = json.loads(
        (project_dir / ".cursor" / "state" / "last-prompt.json").read_text(encoding="utf-8")
    )
    assert "sk-LIVE" not in record["prompt"]
    assert "<redacted>" in record["prompt"]


def test_capture_truncates_long_prompt(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    long_prompt = "Q" * 10000
    _run_main({"session_id": "S3", "prompt": long_prompt}, monkeypatch)
    record = json.loads(
        (project_dir / ".cursor" / "state" / "last-prompt.json").read_text(encoding="utf-8")
    )
    assert len(record["prompt"]) == 8000


def test_capture_missing_session_id(project_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _run_main({"prompt": "hello"}, monkeypatch)
    record = json.loads(
        (project_dir / ".cursor" / "state" / "last-prompt.json").read_text(encoding="utf-8")
    )
    assert record["session_id"] == "unknown"


def test_capture_disabled_env_short_circuits(
    project_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("TLAB_ROUTER_DISABLE", "1")
    out, _err = _run_main({"session_id": "S4", "prompt": "anything"}, monkeypatch)
    assert json.loads(out) == {"continue": True}
    assert not (project_dir / ".cursor" / "state" / "last-prompt.json").exists()


def test_capture_always_returns_continue_true_on_empty(
    project_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out, _err = _run_main({}, monkeypatch)
    assert json.loads(out) == {"continue": True}
