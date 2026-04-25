"""beforeShellExecution hook: block obviously destructive commands.

Configured with ``failClosed: true``: if this hook crashes, the shell
command is BLOCKED. So we keep it stdlib-only and trap every error.
"""

from __future__ import annotations

import re
import sys

from _common import allow, ask, deny, read_input

DANGEROUS_PATTERNS = [
    (re.compile(r"\brm\s+-rf?\s+/(?!\w)"), "rm -rf on root (`/`) is forbidden"),
    (re.compile(r"\brm\s+-rf?\s+\$HOME\b"), "rm -rf on $HOME is forbidden"),
    (re.compile(r"\brm\s+-rf?\s+~/?\s"), "rm -rf on ~ is forbidden"),
    (re.compile(r":\(\)\s*\{.*:\|:&\s*\};:"), "fork bomb pattern detected"),
    (re.compile(r"\bmkfs\.\w+"), "filesystem format command is forbidden"),
    (re.compile(r"\bdd\s+if=.*of=/dev/(sd|nvme|hd)"), "dd to a raw device is forbidden"),
    (re.compile(r">\s*/dev/sd[a-z]"), "redirecting to raw disk is forbidden"),
    (re.compile(r"\bchmod\s+777\s+/"), "chmod 777 on root is forbidden"),
]

ASK_PATTERNS = [
    (re.compile(r"\bgit\s+push\s+.*--force\b"), "force push requires confirmation"),
    (re.compile(r"\bgit\s+push\s+.*-f\b"), "force push requires confirmation"),
    (re.compile(r"\bgit\s+reset\s+--hard\b"), "hard reset requires confirmation"),
    (re.compile(r"\bdocker\s+compose\s+down\s+-v\b"),
     "compose down -v destroys volumes (DuckDB data) — confirm"),
    (re.compile(r"\bRISK_BYPASS\b|--no-risk\b|skip[_-]?risk\b|bypass[_-]?risk\b"),
     "risk-bypass flag detected — this is a release blocker"),
    (re.compile(r"--broker\s+(binance|coinbase)\b(?!.*--testnet|.*--sandbox)"),
     "live broker without --testnet/--sandbox — confirm intent"),
]


def main() -> None:
    payload = read_input()
    command = (payload.get("command") or "").strip()
    if not command:
        allow()
        return

    for pat, reason in DANGEROUS_PATTERNS:
        if pat.search(command):
            deny(
                user_message=f"Blocked dangerous command: {reason}",
                agent_message=(
                    f"The command `{command[:200]}` was blocked: {reason}. "
                    "If this is intentional, the user must run it manually."
                ),
            )
            return

    for pat, reason in ASK_PATTERNS:
        if pat.search(command):
            ask(
                user_message=f"Confirm: {reason}",
                agent_message=(
                    f"`{command[:200]}` requires user confirmation: {reason}."
                ),
            )
            return

    allow()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"block_dangerous_shell hook error: {exc}\n")
        deny(
            user_message="Hook crashed; command blocked by failClosed policy.",
            agent_message=(
                "block_dangerous_shell.py crashed and the hook is configured "
                "failClosed=true. Investigate the hook before retrying."
            ),
        )
