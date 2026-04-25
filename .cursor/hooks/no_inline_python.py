"""beforeShellExecution hook: redirect inline Python to a saved script.

Reads the standard Cursor ``beforeShellExecution`` JSON payload from stdin and
checks the ``command`` field for inline Python execution patterns:

    * ``python -c "..."`` / ``python3 -c "..."`` (any short flag combo with ``c``)
    * heredoc-style ``python << EOF ... EOF`` invocations
    * heredocs whose body is piped into ``python``
    * PowerShell here-strings piped into ``python``

When a pattern matches, the hook returns ``permission: "ask"`` with a message
pointing the agent at the ``script-first-python`` skill so the snippet gets
saved under ``scripts/`` and reused later instead of being regenerated.

Otherwise the hook calls :func:`allow` and exits 0.

The script also supports a ``--self-test`` mode for offline verification:

    python .cursor/hooks/no_inline_python.py --self-test

Exits 0 when every internal case behaves as expected, 1 otherwise.

This hook is intentionally ``failClosed: false``. A crash here must never
block legitimate shell execution; the worst case is a missed warning.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable

from _common import allow, ask, read_input

# Patterns that indicate inline Python code rather than a saved script.
# Each entry is (regex, human-readable label).
INLINE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # python -c "..."  /  python3 -c '...'  /  python -uc ...
    (
        re.compile(r"\bpython3?(?:\.\d+)?\b\s+-[A-Za-z]*c\b"),
        "python -c \"...\"",
    ),
    # python <<EOF ... (heredoc beginning on the python line)
    (
        re.compile(
            r"\bpython3?(?:\.\d+)?\b[^\n]{0,200}<<-?\s*[\'\"]?\w+",
            re.DOTALL,
        ),
        "python <<EOF heredoc",
    ),
    # heredoc whose stream is piped into python (cat <<EOF ... | python)
    (
        re.compile(
            r"<<-?\s*[\'\"]?\w+[\s\S]+?\|\s*python3?(?:\.\d+)?\b",
            re.DOTALL,
        ),
        "heredoc piped into python",
    ),
    # PowerShell-style here-string piped into python: @"..."@ | python
    (
        re.compile(
            r"@[\'\"][\s\S]+?[\'\"]@\s*\|\s*python3?(?:\.\d+)?\b",
            re.DOTALL,
        ),
        "PowerShell here-string piped into python",
    ),
]


REDIRECT_AGENT_MESSAGE = (
    "Inline Python detected ({label}). The trading-lab repo persists generated "
    "Python via the `script-first-python` skill instead of regenerating it on "
    "every session. Read `.cursor/skills/script-first-python/SKILL.md`, then "
    "either:\n"
    "  1. Search `scripts/` and `SCRIPTS.md` for an existing script that does "
    "this, OR\n"
    "  2. Save the snippet to `scripts/<verb>-<noun>.py` with argparse + "
    "docstring, add a row to `SCRIPTS.md`, and run that file instead.\n"
    "If this really is a one-line probe and saving a file would be overkill, "
    "the user can approve this prompt — but default to writing the file."
)

REDIRECT_USER_MESSAGE = (
    "Hook flagged inline Python ({label}). Allow only if this is a trivial "
    "one-shot probe; otherwise ask the agent to save it under scripts/."
)


def classify(command: str) -> tuple[bool, str]:
    """Return ``(is_inline, label)`` for a shell command string."""
    for pattern, label in INLINE_PATTERNS:
        if pattern.search(command):
            return True, label
    return False, ""


def run_hook() -> None:
    payload = read_input()
    command = ""
    if isinstance(payload, dict):
        command = str(payload.get("command", "") or "")

    if not command:
        allow()
        return

    is_inline, label = classify(command)
    if not is_inline:
        allow()
        return

    ask(
        user_message=REDIRECT_USER_MESSAGE.format(label=label),
        agent_message=REDIRECT_AGENT_MESSAGE.format(label=label),
    )


# --- self-test --------------------------------------------------------------

SELF_TEST_CASES: list[tuple[str, bool, str]] = [
    # (command, expect_inline, note)
    ("python -c \"print('hi')\"", True, "basic python -c"),
    ("python3 -c 'print(1)'", True, "python3 -c"),
    ("python -uc 'print(1)'", True, "python with combined flags ending in c"),
    (
        "python <<EOF\nprint('hi')\nEOF",
        True,
        "python heredoc",
    ),
    (
        "cat <<'PY' | python\nprint(1)\nPY",
        True,
        "cat heredoc piped to python",
    ),
    (
        "@\"\nprint('hi')\n\"@ | python",
        True,
        "powershell here-string piped to python",
    ),
    ("python --version", False, "version probe"),
    ("python -m pytest -q", False, "module invocation"),
    ("python -m pip install -e .", False, "pip install"),
    ("python scripts/dump-features.py --rows 20", False, "saved script"),
    ("python -m backtests.run --config configs/x.yaml", False, "module run"),
    ("ruff check .", False, "non-python tool"),
    ("git status", False, "no python at all"),
    ("python -m foo --command", False, "innocent token containing 'c'"),
]


def run_self_test(cases: Iterable[tuple[str, bool, str]] = SELF_TEST_CASES) -> int:
    failures: list[str] = []
    total = 0
    for command, expected, note in cases:
        total += 1
        is_inline, label = classify(command)
        if is_inline != expected:
            failures.append(
                f"  [FAIL] {note!r}: expected inline={expected}, "
                f"got inline={is_inline} (label={label!r})\n"
                f"         command={command!r}"
            )
        else:
            sys.stdout.write(f"  [ok]   {note}\n")

    if failures:
        sys.stdout.write("\n".join(failures) + "\n")
        sys.stdout.write(f"\nFAILED ({len(failures)} of {total})\n")
        return 1

    sys.stdout.write(f"\nPASSED ({total} cases)\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run internal regex test cases instead of reading stdin.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    try:
        run_hook()
    except Exception as exc:
        sys.stderr.write(f"no_inline_python hook error: {exc}\n")
        # Fall back to allow so we never block on our own bug.
        allow()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
