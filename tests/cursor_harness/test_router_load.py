"""Tests for ``_router_core.load_routing_table``."""

from __future__ import annotations

import json
from pathlib import Path


def _write(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj), encoding="utf-8")


def test_load_returns_none_when_missing(project_dir: Path) -> None:
    from _router_core import load_routing_table

    assert load_routing_table(project_dir / "missing.json") is None


def test_load_returns_none_when_malformed(project_dir: Path) -> None:
    from _router_core import load_routing_table

    bad = project_dir / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    assert load_routing_table(bad) is None


def test_load_returns_none_when_wrong_version(project_dir: Path) -> None:
    from _router_core import load_routing_table

    p = project_dir / "rt.json"
    _write(p, {"version": 99, "rules": []})
    assert load_routing_table(p) is None


def test_load_returns_none_when_no_rules_list(project_dir: Path) -> None:
    from _router_core import load_routing_table

    p = project_dir / "rt.json"
    _write(p, {"version": 1, "rules": "oops"})
    assert load_routing_table(p) is None


def test_load_drops_duplicate_ids(project_dir: Path) -> None:
    from _router_core import load_routing_table

    p = project_dir / "rt.json"
    _write(
        p,
        {
            "version": 1,
            "rules": [
                {
                    "id": "dup",
                    "priority": 10,
                    "match": {"prompt_regex": ["foo"]},
                    "snippets": [{"path": "AGENTS.md", "max_chars": 100}],
                },
                {
                    "id": "dup",
                    "priority": 20,
                    "match": {"prompt_regex": ["bar"]},
                    "snippets": [{"path": "AGENTS.md", "max_chars": 100}],
                },
            ],
        },
    )
    table = load_routing_table(p)
    assert table is not None
    assert len(table["rules"]) == 1
    assert table["rules"][0]["priority"] == 10


def test_load_drops_bad_regex_but_keeps_rest(project_dir: Path) -> None:
    from _router_core import load_routing_table

    p = project_dir / "rt.json"
    _write(
        p,
        {
            "version": 1,
            "rules": [
                {
                    "id": "mixed",
                    "priority": 1,
                    "match": {"prompt_regex": ["[broken", "good_pattern"]},
                    "snippets": [{"path": "AGENTS.md", "max_chars": 100}],
                }
            ],
        },
    )
    table = load_routing_table(p)
    assert table is not None
    rule = table["rules"][0]
    assert rule["match"]["prompt_regex"] == ["good_pattern"]


def test_load_rejects_path_traversal(project_dir: Path) -> None:
    from _router_core import load_routing_table

    p = project_dir / "rt.json"
    _write(
        p,
        {
            "version": 1,
            "rules": [
                {
                    "id": "traversal",
                    "priority": 1,
                    "match": {"prompt_regex": ["x"]},
                    "snippets": [{"path": "../etc/passwd", "max_chars": 10}],
                }
            ],
        },
    )
    table = load_routing_table(p)
    assert table is not None
    assert table["rules"] == []


def test_load_rejects_absolute_path(project_dir: Path) -> None:
    from _router_core import load_routing_table

    p = project_dir / "rt.json"
    _write(
        p,
        {
            "version": 1,
            "rules": [
                {
                    "id": "abs",
                    "priority": 1,
                    "match": {"prompt_regex": ["x"]},
                    "snippets": [{"path": "/etc/passwd", "max_chars": 10}],
                }
            ],
        },
    )
    table = load_routing_table(p)
    assert table is not None
    assert table["rules"] == []
