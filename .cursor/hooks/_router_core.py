"""Pure routing core for ``prompt_context_router``.

All filesystem and stdin/stdout work lives in the hook entry-point
modules. This module is a deterministic library of small functions
the hooks compose.

Entry points:

- ``load_routing_table(path)`` — parse + validate the routing-table
  JSON; drop bad rules with a stderr warning.
- ``rule_matches(rule, ...)`` — evaluate a single rule's match block.
- ``excerpt(path, anchor, max_chars, project_dir)`` — read a bounded
  excerpt of a steering file.
- ``prune_memory(memory, *, now, ttl_hours)`` — drop expired
  ``InjectedSnippet`` entries.
- ``route(...)`` — the deterministic top-level function: decides
  what to inject, returns updated memory and a log record.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from _common import SECRET_KEYS
from _router_io import read_json
from _router_types import (
    InjectedSnippet,
    InjectedSnippetSummary,
    LastPromptRecord,
    MatchClause,
    RouterLogRecord,
    RoutingRule,
    RoutingTable,
    SessionMemoryFile,
    SnippetSpec,
)

ROUTING_TABLE_VERSION = 1
SESSION_MEMORY_VERSION = 1
DEFAULT_TTL_HOURS = 24
TRUNCATION_MARKER = "\n\n... [truncated]"
HEADER_TEMPLATE = "## Auto-loaded: {label} (rule: {rule_id})\n\n"


def _warn(msg: str) -> None:
    sys.stderr.write(f"[router] {msg}\n")


def load_routing_table(path: Path) -> RoutingTable | None:
    """Load and validate the routing-table JSON.

    Returns ``None`` if the file is missing, malformed, or has the
    wrong top-level shape. Individual rules with invalid regex or
    unsafe paths are dropped with a stderr warning; remaining rules
    are returned.
    """
    raw = read_json(path)
    if not isinstance(raw, dict):
        _warn(f"routing table missing or not a JSON object: {path}")
        return None
    if raw.get("version") != ROUTING_TABLE_VERSION:
        _warn(f"routing table version != {ROUTING_TABLE_VERSION}: {path}")
        return None
    rules_raw = raw.get("rules")
    if not isinstance(rules_raw, list):
        _warn("routing table has no 'rules' list")
        return None

    seen_ids: set[str] = set()
    valid_rules: list[RoutingRule] = []
    for entry in rules_raw:
        rule = _validate_rule(entry, seen_ids)
        if rule is not None:
            valid_rules.append(rule)
            seen_ids.add(rule["id"])
    return {"version": ROUTING_TABLE_VERSION, "rules": valid_rules}


def _validate_rule(entry: Any, seen_ids: set[str]) -> RoutingRule | None:  # noqa: PLR0911
    if not isinstance(entry, dict):
        _warn("rule entry is not an object; skipping")
        return None
    rule_id = entry.get("id")
    if not isinstance(rule_id, str) or not rule_id:
        _warn("rule missing string 'id'; skipping")
        return None
    if rule_id in seen_ids:
        _warn(f"duplicate rule id '{rule_id}'; skipping later occurrence")
        return None

    priority = entry.get("priority", 0)
    if not isinstance(priority, int):
        _warn(f"rule '{rule_id}' priority not int; defaulting to 0")
        priority = 0

    match_raw = entry.get("match", {})
    if not isinstance(match_raw, dict):
        _warn(f"rule '{rule_id}' has non-object match; skipping")
        return None
    match = _validate_match_clause(match_raw, rule_id)
    if match is None:
        return None

    snippets_raw = entry.get("snippets", [])
    if not isinstance(snippets_raw, list) or not snippets_raw:
        _warn(f"rule '{rule_id}' has no snippets; skipping")
        return None
    snippets: list[SnippetSpec] = []
    for snip in snippets_raw:
        validated = _validate_snippet(snip, rule_id)
        if validated is not None:
            snippets.append(validated)
    if not snippets:
        return None

    return {
        "id": rule_id,
        "priority": priority,
        "description": str(entry.get("description", "")),
        "match": match,
        "snippets": snippets,
    }


def _validate_match_clause(raw: dict[str, Any], rule_id: str) -> MatchClause | None:
    out: MatchClause = {}
    list_keys = (
        "prompt_regex",
        "tool_input_regex",
        "tool_output_regex",
        "agent_message_regex",
        "tool_name_in",
    )
    for key in list_keys:
        if key not in raw:
            continue
        value = raw[key]
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            _warn(f"rule '{rule_id}' match.{key} not a list[str]; ignoring key")
            continue
        if key.endswith("_regex"):
            valid: list[str] = []
            for pat in value:
                try:
                    re.compile(pat)
                except re.error as exc:
                    _warn(f"rule '{rule_id}' bad regex in {key}: {exc!r}")
                    continue
                valid.append(pat)
            if valid:
                out[key] = valid  # type: ignore[literal-required]
        else:
            out[key] = list(value)  # type: ignore[literal-required]
    if not out:
        _warn(f"rule '{rule_id}' has no usable match keys; skipping")
        return None
    return out


def _validate_snippet(raw: Any, rule_id: str) -> SnippetSpec | None:
    if not isinstance(raw, dict):
        _warn(f"rule '{rule_id}' snippet not an object; skipping")
        return None
    path = raw.get("path")
    if not isinstance(path, str) or not path:
        _warn(f"rule '{rule_id}' snippet missing 'path'; skipping")
        return None
    if path.startswith(("/", "\\")) or ".." in Path(path).parts:
        _warn(f"rule '{rule_id}' snippet path '{path}' rejected (traversal)")
        return None
    max_chars = raw.get("max_chars", 1200)
    if not isinstance(max_chars, int) or max_chars <= 0:
        _warn(f"rule '{rule_id}' snippet max_chars invalid; defaulting to 1200")
        max_chars = 1200
    anchor_raw = raw.get("anchor")
    anchor: str | None = anchor_raw if isinstance(anchor_raw, str) else None
    return {"path": path, "anchor": anchor, "max_chars": max_chars}


def stringify_tool_input(tool_input: Any) -> str:
    """Flatten ``tool_input`` to a search string, redacting secret-like keys."""
    if isinstance(tool_input, str):
        return tool_input
    if isinstance(tool_input, dict):
        parts: list[str] = []
        for key, value in tool_input.items():
            key_lc = str(key).lower()
            if any(secret in key_lc for secret in SECRET_KEYS):
                continue
            parts.append(f"{key}={_to_str(value)}")
        return " ".join(parts)
    return _to_str(tool_input)


def _to_str(value: Any) -> str:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return str(value)
    try:
        return json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError):
        return repr(value)


def rule_matches(
    rule: RoutingRule,
    *,
    prompt: str,
    tool_name: str,
    tool_input_str: str,
    tool_output: str,
    agent_message: str,
) -> bool:
    """Return True if any present trigger key matches its target.

    Trigger keys (``prompt_regex``, ``tool_input_regex``,
    ``tool_output_regex``, ``agent_message_regex``) are OR-combined:
    any one matching fires the rule. Within a list-valued key,
    elements are OR-combined as well. ``tool_name_in`` is a filter,
    not a trigger: when present, the current tool name must be in the
    list (AND with the trigger result). An empty clause never fires.
    """
    match = rule["match"]
    if not match:
        return False

    tool_filter = match.get("tool_name_in")
    if tool_filter is not None and tool_name not in tool_filter:
        return False

    trigger_targets: dict[str, str] = {
        "prompt_regex": prompt,
        "tool_input_regex": tool_input_str,
        "tool_output_regex": tool_output,
        "agent_message_regex": agent_message,
    }
    triggers_present = False
    for field, target in trigger_targets.items():
        patterns = match.get(field)  # type: ignore[literal-required]
        if patterns is None:
            continue
        triggers_present = True
        if _any_regex_matches(patterns, target):
            return True

    return not triggers_present and tool_filter is not None


def _any_regex_matches(patterns: Iterable[str], target: str) -> bool:
    if not target:
        return False
    for pat in patterns:
        try:
            if re.search(pat, target):
                return True
        except re.error:
            continue
    return False


def excerpt(
    path: str,
    anchor: str | None,
    max_chars: int,
    project_dir: Path,
) -> str | None:
    """Read a bounded excerpt of a steering file.

    - ``anchor=None`` → first ``max_chars`` of the file.
    - ``anchor='## Header'`` → from that header to the next top-level
      ``## `` header (exclusive) or EOF, capped at ``max_chars``.

    Returns ``None`` if the file is missing/unreadable, or if the
    anchor is supplied but not found.
    """
    full = (project_dir / path).resolve()
    try:
        project_root = project_dir.resolve()
        full.relative_to(project_root)
    except (OSError, ValueError):
        return None
    try:
        text = full.read_text(encoding="utf-8")
    except OSError:
        return None

    if anchor:
        text = _slice_section(text, anchor)
        if text is None:
            return None

    if len(text) <= max_chars:
        return text
    cut = max(0, max_chars - len(TRUNCATION_MARKER))
    return text[:cut] + TRUNCATION_MARKER


def _slice_section(text: str, anchor: str) -> str | None:
    needle = anchor if anchor.startswith("#") else f"## {anchor}"
    idx = text.find(needle)
    if idx == -1:
        return None
    rest = text[idx:]
    next_idx = rest.find("\n## ", 1)
    if next_idx == -1:
        return rest
    return rest[:next_idx]


def prune_memory(
    memory: SessionMemoryFile,
    *,
    now: datetime,
    ttl_hours: int = DEFAULT_TTL_HOURS,
) -> SessionMemoryFile:
    """Drop ``InjectedSnippet`` entries older than ``ttl_hours``."""
    cutoff = now - timedelta(hours=ttl_hours)
    cleaned: dict[str, list[InjectedSnippet]] = {}
    for sid, entries in memory.get("sessions", {}).items():
        kept: list[InjectedSnippet] = []
        for entry in entries:
            ts = _parse_iso(entry.get("injected_at", ""))
            if ts is None or ts >= cutoff:
                kept.append(entry)
        if kept:
            cleaned[sid] = kept
    return {"version": SESSION_MEMORY_VERSION, "sessions": cleaned}


def _parse_iso(value: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def empty_memory() -> SessionMemoryFile:
    return {"version": SESSION_MEMORY_VERSION, "sessions": {}}


def empty_log_record(*, session_id: str, tool_name: str, now: datetime) -> RouterLogRecord:
    return {
        "timestamp": now.isoformat(),
        "session_id": session_id,
        "tool_name": tool_name,
        "matched_rule_ids": [],
        "injected_snippets": [],
        "total_chars": 0,
        "skip_reason": None,
    }


def route(
    *,
    hook_input: dict[str, Any],
    last_prompt: LastPromptRecord | None,
    routing_table: RoutingTable,
    session_memory: SessionMemoryFile,
    budget_chars: int,
    project_dir: Path,
    now: datetime,
) -> tuple[str, SessionMemoryFile, RouterLogRecord]:
    """Compute the ``additional_context`` to inject for one tool call.

    Pure function (no I/O). Returns ``(text, updated_memory, log)``.
    """
    tool_name = str(hook_input.get("tool_name") or "")
    tool_input_str = stringify_tool_input(hook_input.get("tool_input"))
    tool_output = _to_str(hook_input.get("tool_output", ""))
    agent_message = str(hook_input.get("agent_message") or "")
    prompt = (last_prompt or {}).get("prompt", "") if last_prompt else ""
    session_id = (last_prompt or {}).get("session_id", "unknown") if last_prompt else "unknown"

    log = empty_log_record(session_id=session_id, tool_name=tool_name, now=now)
    memory = prune_memory(session_memory, now=now)

    if budget_chars <= 0:
        return "", memory, log

    matched: list[RoutingRule] = [
        rule
        for rule in routing_table["rules"]
        if rule_matches(
            rule,
            prompt=prompt,
            tool_name=tool_name,
            tool_input_str=tool_input_str,
            tool_output=tool_output,
            agent_message=agent_message,
        )
    ]
    matched.sort(key=lambda r: r["priority"], reverse=True)
    log["matched_rule_ids"] = [r["id"] for r in matched]
    if not matched:
        return "", memory, log

    session_entries = list(memory["sessions"].get(session_id, []))
    fragments: list[str] = []
    summaries: list[InjectedSnippetSummary] = []
    used = 0
    new_entries: list[InjectedSnippet] = []
    skipped_dedupe = 0

    for rule in matched:
        for snip in rule["snippets"]:
            text = excerpt(
                snip["path"],
                snip.get("anchor"),
                snip["max_chars"],
                project_dir,
            )
            if text is None:
                continue
            digest = _sha256(text)
            if _is_duplicate(session_entries + new_entries, rule["id"], snip, digest):
                skipped_dedupe += 1
                continue
            label = _label(snip)
            block = HEADER_TEMPLATE.format(label=label, rule_id=rule["id"]) + text + "\n"
            cost = len(block)
            if used + cost > budget_chars:
                continue
            fragments.append(block)
            used += cost
            summaries.append({"path": snip["path"], "anchor": snip.get("anchor"), "chars": cost})
            new_entries.append(
                {
                    "rule_id": rule["id"],
                    "path": snip["path"],
                    "anchor": snip.get("anchor"),
                    "sha256": digest,
                    "injected_at": now.isoformat(),
                }
            )

    if new_entries:
        memory["sessions"].setdefault(session_id, []).extend(new_entries)
    log["injected_snippets"] = summaries
    log["total_chars"] = used
    if not fragments and skipped_dedupe:
        log["skip_reason"] = "deduplicated"
    elif not fragments and matched:
        _warn(
            f"router: matched {len(matched)} rule(s) but injected none "
            f"(budget={budget_chars}, dedupe_skipped={skipped_dedupe})"
        )
        log["skip_reason"] = "budget_exceeded" if not skipped_dedupe else "deduplicated"

    return "".join(fragments), memory, log


def _label(snip: SnippetSpec) -> str:
    base = snip["path"]
    anchor = snip.get("anchor")
    if anchor:
        return f"{base} ({anchor})"
    return base


def _is_duplicate(
    entries: Iterable[InjectedSnippet],
    rule_id: str,
    snip: SnippetSpec,
    digest: str,
) -> bool:
    target_path = snip["path"]
    target_anchor = snip.get("anchor")
    for entry in entries:
        if (
            entry["rule_id"] == rule_id
            and entry["path"] == target_path
            and entry.get("anchor") == target_anchor
            and entry["sha256"] == digest
        ):
            return True
    return False
