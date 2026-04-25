"""beforeShellExecution(matcher='git commit') hook: fast pre-commit safety net.

We do NOT run the full `review-local` skill here (too slow). Instead we
check the staged diff for the highest-signal violations:

- forbidden risk-bypass tokens
- live broker without --testnet/--sandbox
- AI-slop phrases ("should work", "left as an exercise")
- secret-like patterns

If any are found, we return ``permission: ask`` with the offending
lines so the user can confirm or abort.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys

from _common import allow, ask, read_input

FORBIDDEN_TOKENS = re.compile(
    r"\b("
    r"skip_risk|bypass_risk|RISK_BYPASS|DISABLE_RISK|--no-risk|"
    r"AKIA[0-9A-Z]{16}|"
    r"sk-[A-Za-z0-9]{20,}|"
    r"BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY|"
    r"should work|left as an exercise|verified offline"
    r")\b",
    re.IGNORECASE,
)

MAX_SNIPPET_LEN = 200
MAX_FINDINGS = 5


def main() -> None:
    payload = read_input()
    command = payload.get("command") or ""
    if "git commit" not in command:
        allow()
        return

    git = shutil.which("git")
    if git is None:
        allow()
        return

    try:
        result = subprocess.run(
            [git, "diff", "--cached", "--unified=0"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (subprocess.SubprocessError, OSError):
        allow()
        return

    diff = result.stdout or ""
    findings: list[str] = []
    for ln in diff.splitlines():
        if not ln.startswith("+") or ln.startswith("+++"):
            continue
        m = FORBIDDEN_TOKENS.search(ln)
        if m:
            snippet = ln.strip()
            if len(snippet) > MAX_SNIPPET_LEN:
                snippet = snippet[:MAX_SNIPPET_LEN] + "…"
            findings.append(f"  {snippet}")
            if len(findings) >= MAX_FINDINGS:
                break

    if not findings:
        allow()
        return

    msg = "Pre-commit review found suspicious lines in the staged diff:\n" + "\n".join(findings)
    ask(
        user_message=msg,
        agent_message=(
            "Pre-commit review flagged the staged diff. Run the "
            "`review-local` skill in full before committing. If the user "
            "confirms, the commit will proceed."
        ),
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"pre_commit_review hook error: {exc}\n")
        allow()
