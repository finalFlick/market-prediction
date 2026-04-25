"""Sanity tests for the committed ``.cursor/context-router.json``.

These run against the real, version-controlled file so PR-time
breakage is caught early.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROUTING_TABLE = ROOT / ".cursor" / "context-router.json"


def test_routing_table_parses_as_json() -> None:
    raw = json.loads(ROUTING_TABLE.read_text(encoding="utf-8"))
    assert raw["version"] == 1
    assert isinstance(raw["rules"], list)
    assert len(raw["rules"]) >= 8


def test_routing_table_rule_ids_are_unique() -> None:
    raw = json.loads(ROUTING_TABLE.read_text(encoding="utf-8"))
    ids = [r["id"] for r in raw["rules"]]
    assert len(ids) == len(set(ids)), f"duplicate rule ids: {ids}"


def test_routing_table_required_v1_rule_ids_present() -> None:
    raw = json.loads(ROUTING_TABLE.read_text(encoding="utf-8"))
    required = {
        "risk-policy",
        "evaluation-gates",
        "signal-research",
        "data-ingest",
        "frontend-dashboard",
        "infra-deployment",
        "llm-isolation",
        "spec-workflow",
    }
    ids = {r["id"] for r in raw["rules"]}
    missing = required - ids
    assert not missing, f"v1 routing table missing required rules: {missing}"


def test_routing_table_regexes_compile() -> None:
    raw = json.loads(ROUTING_TABLE.read_text(encoding="utf-8"))
    regex_keys = (
        "prompt_regex",
        "tool_input_regex",
        "tool_output_regex",
        "agent_message_regex",
    )
    for rule in raw["rules"]:
        for key in regex_keys:
            patterns = rule.get("match", {}).get(key, [])
            for pat in patterns:
                re.compile(pat)


def test_routing_table_snippet_paths_exist() -> None:
    raw = json.loads(ROUTING_TABLE.read_text(encoding="utf-8"))
    missing: list[str] = []
    for rule in raw["rules"]:
        for snip in rule["snippets"]:
            target = ROOT / snip["path"]
            if not target.exists():
                missing.append(f"{rule['id']} -> {snip['path']}")
    assert not missing, f"routing table references missing files: {missing}"


def test_routing_table_no_path_traversal() -> None:
    raw = json.loads(ROUTING_TABLE.read_text(encoding="utf-8"))
    for rule in raw["rules"]:
        for snip in rule["snippets"]:
            path = snip["path"]
            assert not path.startswith(("/", "\\")), f"absolute path: {path}"
            assert ".." not in Path(path).parts, f"traversal in path: {path}"
