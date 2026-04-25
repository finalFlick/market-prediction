"""Tests for ``_router_core.rule_matches``."""

from __future__ import annotations

from typing import cast


def _rule(match: dict, *, rule_id: str = "r", priority: int = 1) -> dict:
    return {
        "id": rule_id,
        "priority": priority,
        "description": "",
        "match": match,
        "snippets": [{"path": "AGENTS.md", "anchor": None, "max_chars": 100}],
    }


def test_prompt_regex_match() -> None:
    from _router_core import rule_matches
    from _router_types import RoutingRule

    rule = cast(RoutingRule, _rule({"prompt_regex": ["(?i)risk"]}))
    assert rule_matches(
        rule,
        prompt="Tighten the risk engine",
        tool_name="Read",
        tool_input_str="",
        tool_output="",
        agent_message="",
    )


def test_tool_input_regex_match() -> None:
    from _router_core import rule_matches
    from _router_types import RoutingRule

    rule = cast(RoutingRule, _rule({"tool_input_regex": [r"risk[\\/]engine\.py"]}))
    assert rule_matches(
        rule,
        prompt="",
        tool_name="Read",
        tool_input_str="path=risk/engine.py",
        tool_output="",
        agent_message="",
    )


def test_tool_name_filter_excludes() -> None:
    from _router_core import rule_matches
    from _router_types import RoutingRule

    rule = cast(
        RoutingRule,
        _rule({"prompt_regex": ["foo"], "tool_name_in": ["Read", "Grep"]}),
    )
    assert not rule_matches(
        rule,
        prompt="foo",
        tool_name="Shell",
        tool_input_str="",
        tool_output="",
        agent_message="",
    )


def test_or_between_keys_or_within_list() -> None:
    """Trigger keys are OR-combined: any one matching fires the rule.

    Within a list-valued key, elements are also OR-combined. The rule
    only fails to fire when **none** of its trigger keys match.
    """
    from _router_core import rule_matches
    from _router_types import RoutingRule

    rule = cast(
        RoutingRule,
        _rule(
            {
                "prompt_regex": ["alpha", "beta"],
                "tool_input_regex": ["target_file"],
            }
        ),
    )
    assert rule_matches(
        rule,
        prompt="alpha here",
        tool_name="Read",
        tool_input_str="opens target_file",
        tool_output="",
        agent_message="",
    )
    assert rule_matches(
        rule,
        prompt="alpha here",
        tool_name="Read",
        tool_input_str="opens other",
        tool_output="",
        agent_message="",
    )
    assert rule_matches(
        rule,
        prompt="gamma",
        tool_name="Read",
        tool_input_str="opens target_file",
        tool_output="",
        agent_message="",
    )
    assert not rule_matches(
        rule,
        prompt="gamma",
        tool_name="Read",
        tool_input_str="opens other",
        tool_output="",
        agent_message="",
    )


def test_tool_name_filter_anded_with_triggers() -> None:
    """``tool_name_in`` filters the rule: trigger must match AND tool must be allowed."""
    from _router_core import rule_matches
    from _router_types import RoutingRule

    rule = cast(
        RoutingRule,
        _rule({"prompt_regex": ["foo"], "tool_name_in": ["Read"]}),
    )
    assert rule_matches(
        rule,
        prompt="foo bar",
        tool_name="Read",
        tool_input_str="",
        tool_output="",
        agent_message="",
    )
    assert not rule_matches(
        rule,
        prompt="foo bar",
        tool_name="Shell",
        tool_input_str="",
        tool_output="",
        agent_message="",
    )


def test_no_match_returns_false() -> None:
    from _router_core import rule_matches
    from _router_types import RoutingRule

    rule = cast(RoutingRule, _rule({"prompt_regex": ["zzz"]}))
    assert not rule_matches(
        rule,
        prompt="completely unrelated",
        tool_name="Read",
        tool_input_str="",
        tool_output="",
        agent_message="",
    )


def test_empty_match_clause_never_fires() -> None:
    from _router_core import rule_matches
    from _router_types import RoutingRule

    rule = cast(RoutingRule, _rule({}))
    assert not rule_matches(
        rule,
        prompt="anything",
        tool_name="Read",
        tool_input_str="",
        tool_output="",
        agent_message="",
    )


def test_agent_message_match() -> None:
    from _router_core import rule_matches
    from _router_types import RoutingRule

    rule = cast(RoutingRule, _rule({"agent_message_regex": ["(?i)kill\\s*switch"]}))
    assert rule_matches(
        rule,
        prompt="",
        tool_name="Read",
        tool_input_str="",
        tool_output="",
        agent_message="Tracing the kill switch path",
    )


def test_stringify_tool_input_skips_secret_keys() -> None:
    from _router_core import stringify_tool_input

    flat = stringify_tool_input(
        {"path": "data.csv", "api_key": "sk-xyz", "token": "abc"}
    )
    assert "data.csv" in flat
    assert "sk-xyz" not in flat
    assert "abc" not in flat


def test_stringify_tool_input_handles_string() -> None:
    from _router_core import stringify_tool_input

    assert stringify_tool_input("just a string") == "just a string"
