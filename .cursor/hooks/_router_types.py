"""Typed contracts for the prompt-context-router hooks.

Stdlib-only TypedDicts. Used by ``_router_core``, ``prompt_capture``,
and ``prompt_context_router`` to keep ``mypy --strict`` happy without
introducing a third-party dependency.

See ``specs/prompt-context-router/design.md`` § Data Models for the
authoritative description of each shape.
"""

from __future__ import annotations

from typing import TypedDict


class LastPromptRecord(TypedDict):
    session_id: str
    prompt: str
    attachments: list[dict[str, object]]
    captured_at: str


class InjectedSnippet(TypedDict):
    rule_id: str
    path: str
    anchor: str | None
    sha256: str
    injected_at: str


class SessionMemoryFile(TypedDict):
    version: int
    sessions: dict[str, list[InjectedSnippet]]


class InjectedSnippetSummary(TypedDict):
    path: str
    anchor: str | None
    chars: int


class RouterLogRecord(TypedDict):
    timestamp: str
    session_id: str
    tool_name: str
    matched_rule_ids: list[str]
    injected_snippets: list[InjectedSnippetSummary]
    total_chars: int
    skip_reason: str | None


class MatchClause(TypedDict, total=False):
    prompt_regex: list[str]
    tool_input_regex: list[str]
    tool_output_regex: list[str]
    agent_message_regex: list[str]
    tool_name_in: list[str]


class SnippetSpec(TypedDict, total=False):
    path: str
    anchor: str | None
    max_chars: int


class RoutingRule(TypedDict):
    id: str
    priority: int
    description: str
    match: MatchClause
    snippets: list[SnippetSpec]


class RoutingTable(TypedDict):
    version: int
    rules: list[RoutingRule]
