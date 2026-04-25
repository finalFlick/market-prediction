"""Tests for ``.cursor/hooks/_router_io.py`` — atomic writes, JSONL helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


def test_atomic_write_then_read_roundtrip(project_dir: Path) -> None:
    from _router_io import atomic_write_json, read_json

    target = project_dir / ".cursor" / "state" / "demo.json"
    payload = {"a": 1, "b": [2, 3]}

    assert atomic_write_json(target, payload) is True
    assert target.exists()
    assert read_json(target) == payload


def test_atomic_write_overwrites_existing_file(project_dir: Path) -> None:
    from _router_io import atomic_write_json, read_json

    target = project_dir / "out.json"
    atomic_write_json(target, {"v": 1})
    atomic_write_json(target, {"v": 2})
    assert read_json(target) == {"v": 2}


def test_read_json_returns_none_on_malformed(project_dir: Path) -> None:
    from _router_io import read_json

    bad = project_dir / "bad.json"
    bad.write_text("not json at all{{{", encoding="utf-8")
    assert read_json(bad) is None


def test_read_json_returns_none_on_missing(project_dir: Path) -> None:
    from _router_io import read_json

    assert read_json(project_dir / "missing.json") is None


def test_append_jsonl_creates_and_appends(project_dir: Path) -> None:
    from _router_io import append_jsonl

    target = project_dir / ".cursor" / "state" / "log.jsonl"
    assert append_jsonl(target, {"i": 1}) is True
    assert append_jsonl(target, {"i": 2}) is True

    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"i": 1}
    assert json.loads(lines[1]) == {"i": 2}


def test_truncate_jsonl_keeps_last_n(project_dir: Path) -> None:
    from _router_io import append_jsonl, truncate_jsonl

    target = project_dir / "long.jsonl"
    for i in range(50):
        append_jsonl(target, {"i": i})

    assert truncate_jsonl(target, max_lines=10) is True
    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 10
    assert json.loads(lines[0]) == {"i": 40}
    assert json.loads(lines[-1]) == {"i": 49}


def test_truncate_jsonl_noop_when_under_cap(project_dir: Path) -> None:
    from _router_io import append_jsonl, truncate_jsonl

    target = project_dir / "short.jsonl"
    for i in range(3):
        append_jsonl(target, {"i": i})

    assert truncate_jsonl(target, max_lines=100) is True
    assert len(target.read_text(encoding="utf-8").splitlines()) == 3


def test_truncate_jsonl_invalid_max_returns_false(project_dir: Path) -> None:
    from _router_io import truncate_jsonl

    target = project_dir / "any.jsonl"
    target.write_text("a\n", encoding="utf-8")
    assert truncate_jsonl(target, max_lines=0) is False


@pytest.mark.parametrize("max_lines", [1, 2, 5])
def test_truncate_jsonl_parametric(project_dir: Path, max_lines: int) -> None:
    from _router_io import append_jsonl, truncate_jsonl

    target = project_dir / f"p{max_lines}.jsonl"
    for i in range(20):
        append_jsonl(target, {"i": i})

    truncate_jsonl(target, max_lines=max_lines)
    lines = target.read_text(encoding="utf-8").splitlines()
    assert len(lines) == max_lines
