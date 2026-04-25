"""beforeMCPExecution hook: gate MCP tool calls that mutate external state.

Configured ``failClosed: true``. We allow read-only MCP calls by default,
ask for confirmation on write-class GitHub operations, and deny anything
that looks like a live trading call.
"""

from __future__ import annotations

import sys

from _common import allow, ask, deny, read_input

WRITE_GITHUB_TOOLS = {
    "create_pull_request",
    "create_or_update_file",
    "push_files",
    "delete_file",
    "merge_pull_request",
    "create_branch",
    "create_repository",
    "fork_repository",
    "create_issue",
    "update_issue",
    "create_release",
}

DENY_TOOLS = {
    "create_order",
    "place_order",
    "cancel_all_orders",
    "transfer",
    "withdraw",
}


def main() -> None:
    payload = read_input()
    tool = (payload.get("tool_name") or "").lower()
    bare = tool.split(":")[-1].split(".")[-1].strip()

    if bare in DENY_TOOLS:
        deny(
            user_message=f"MCP tool `{tool}` looks like a live trading action; blocked.",
            agent_message=(
                f"The MCP tool `{tool}` was blocked. Live trading must go "
                "through `execution.brokers` after passing `risk.engine`. "
                "Direct broker MCP calls are not allowed."
            ),
        )
        return

    if bare in WRITE_GITHUB_TOOLS:
        ask(
            user_message=f"Confirm GitHub write: `{tool}`",
            agent_message=(
                f"The MCP tool `{tool}` writes to GitHub. Confirm this is "
                "intentional; do not call it as a side-effect of exploration."
            ),
        )
        return

    allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"guard_mcp_writes hook error: {exc}\n")
        deny(
            user_message="MCP guard hook crashed; call blocked by failClosed policy.",
            agent_message=(
                "guard_mcp_writes.py crashed and the hook is configured "
                "failClosed=true. Investigate before retrying."
            ),
        )
