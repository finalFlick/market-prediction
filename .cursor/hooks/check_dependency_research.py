"""Hook: prompt for confirmation when a dependency is added or installed.

Cursor calls this script for two events:

* ``beforeShellExecution`` — inspects the ``command`` field for
  Python (``pip``, ``python -m pip``, ``uv``, ``poetry``, ``conda``,
  ``mamba``) and Node (``npm``, ``yarn``, ``pnpm``) install commands.
  When at least one new package name is detected, the hook returns
  ``permission: "ask"`` with an agent_message pointing to the
  ``library-research`` rule.

* ``afterFileEdit`` — inspects edits to manifest files
  (``pyproject.toml``, ``requirements*.txt``, ``package.json``) for
  added dependency lines. When found, the hook writes an audit record
  to ``.cursor/state/dependency-touches.jsonl`` and returns an
  ``agent_message`` reminder. It never blocks the edit (afterFileEdit
  cannot deny).

The hook does not — and cannot — verify that a web search actually
happened. It only fires at the moment of the action with a reminder
to consult the rule. The user is expected to approve only after
seeing research evidence in the agent's response.

Self-test:

    python .cursor/hooks/check_dependency_research.py --self-test

Exits 0 if every internal case behaves as expected, 1 otherwise.

This hook is intentionally **not** ``failClosed: true``. A crash here
must never block legitimate work; it falls back to allow.
"""

from __future__ import annotations

import argparse
import re
import shlex
import sys
from collections.abc import Iterable
from typing import Any

from _common import (
    STATE_DIR,
    allow,
    append_jsonl,
    ask,
    ensure_state,
    now_iso,
    read_input,
    write_output,
)

MIN_TOKENS_FOR_PYTHON_M = 2
MAX_LINES_IN_AGENT_MESSAGE = 10

# --- shell command classification -------------------------------------------

# Each entry: (command verb regex tested against tokens, label, package_manager_id).
# The verb pattern is anchored to two consecutive tokens so we don't false-fire
# on substrings (e.g. a script named ``pip-install``).
INSTALL_VERBS: tuple[tuple[tuple[str, ...], str, str], ...] = (
    (("pip", "install"), "pip install", "pip"),
    (("pip3", "install"), "pip3 install", "pip"),
    (("uv", "add"), "uv add", "uv"),
    (("uv", "pip", "install"), "uv pip install", "uv"),
    (("poetry", "add"), "poetry add", "poetry"),
    (("conda", "install"), "conda install", "conda"),
    (("mamba", "install"), "mamba install", "conda"),
    (("npm", "install"), "npm install", "npm"),
    (("npm", "i"), "npm i", "npm"),
    (("npm", "add"), "npm add", "npm"),
    (("yarn", "add"), "yarn add", "yarn"),
    (("pnpm", "add"), "pnpm add", "pnpm"),
    (("pnpm", "install"), "pnpm install", "pnpm"),
    (("pnpm", "i"), "pnpm i", "pnpm"),
)

# Tokens that look like install args but do NOT introduce a new package:
#  - flags:                          ``-e``, ``--upgrade``
#  - paths to local source:          ``.``, ``./``, ``../foo``, ``/abs/path``,
#                                    ``C:\\path``
#  - requirements files (handled    via -r/--requirement which is a flag with
#    an attached value)
#  - environment / setup verbs       (``-e .`` editable install)
NON_PACKAGE_TOKEN_RE = re.compile(
    r"""
    ^(
        -.*                  # flag
      | \.{1,2}(/.*)?        # ., .., ./..., ../foo
      | /.*                  # /abs/path
      | [A-Za-z]:[\\/].*     # C:\path or C:/path
      | \w+\.(txt|toml|cfg|in|lock)$  # local config files
    )$
    """,
    re.VERBOSE,
)

# Tokens that immediately follow a flag and consume its value
# (we drop them rather than treat them as packages).
VALUE_FLAGS = {
    "-r",
    "--requirement",
    "-c",
    "--constraint",
    "-t",
    "--target",
    "--prefix",
    "--root",
    "--index-url",
    "--extra-index-url",
    "--find-links",
    "-f",
    "--registry",
    "--save-prefix",
    "--workspace",
    "-w",
}


def _tokenize(command: str) -> list[str]:
    """Split a shell command into tokens, tolerating quoting issues."""
    try:
        return shlex.split(command, posix=True)
    except ValueError:
        # Fall back to whitespace split — the regex paths only need a rough cut.
        return command.split()


def _match_install_verb(
    tokens: list[str],
) -> tuple[str, str, int] | None:
    """Return ``(label, package_manager, args_start_index)`` or ``None``.

    Skips a leading ``python``/``python3 -m`` so ``python -m pip install x``
    is recognized as ``pip install``.
    """
    if not tokens:
        return None

    i = 0

    # Strip leading ``python -m`` / ``python3 -m`` so ``-m pip install`` works.
    if (
        tokens[0] in {"python", "python3"}
        or re.match(r"^python3?\.\d+$", tokens[0])
    ) and len(tokens) >= MIN_TOKENS_FOR_PYTHON_M and tokens[1] == "-m":
        i = MIN_TOKENS_FOR_PYTHON_M

    head = tokens[i:]
    for verb_tokens, label, pkg_manager in INSTALL_VERBS:
        n = len(verb_tokens)
        if len(head) < n:
            continue
        if tuple(head[:n]) == verb_tokens:
            return label, pkg_manager, i + n
    return None


def _extract_packages(args: list[str]) -> list[str]:
    """Pull package-like positional args out of a list of install args."""
    packages: list[str] = []
    skip_next = False
    for token in args:
        if skip_next:
            skip_next = False
            continue
        if token in VALUE_FLAGS:
            skip_next = True
            continue
        # `--flag=value` forms are flags, not packages.
        if token.startswith("-"):
            continue
        if NON_PACKAGE_TOKEN_RE.match(token):
            continue
        packages.append(token)
    return packages


def classify_command(command: str) -> tuple[bool, str, list[str]]:
    """Return ``(is_install, label, packages)`` for a shell command string.

    ``is_install`` is True only when the verb matches AND at least one
    package-like positional arg was found. Pure ``npm install`` (no args)
    only resolves the existing manifest and is not flagged.
    """
    tokens = _tokenize(command)
    matched = _match_install_verb(tokens)
    if matched is None:
        return False, "", []
    label, _pkg_manager, args_start = matched
    packages = _extract_packages(tokens[args_start:])
    if not packages:
        return False, label, []
    return True, label, packages


# --- manifest edit classification -------------------------------------------

MANIFEST_PATH_FRAGMENTS = (
    "/pyproject.toml",
    "\\pyproject.toml",
    "/package.json",
    "\\package.json",
    "/requirements.txt",
    "\\requirements.txt",
)
MANIFEST_NAME_RE = re.compile(r"requirements[\w.\-]*\.txt$")

# Heuristics for "this added line introduces a dependency":
DEP_HINT_PATTERNS = (
    re.compile(r'^\s*"[^"]+"\s*:\s*"[\^~>=<]?[\d*x]'),  # package.json: "x": "1.0"
    re.compile(r"^\s*[\w.\-]+\s*[~=<>!]=?\s*[\d*x]"),  # requirements.txt name==1.2
    re.compile(r'^\s*[\w.\-]+\s*=\s*"[\^~>=<]?[\d*x]'),  # poetry: name = "^1.0"
    re.compile(r'^\s*"[\w.\-\[\]]+[~=<>!\^]'),  # pep621: "pkg>=1.0"
    re.compile(r'^\s*"[\w.\-]+",?\s*$'),  # pep621: "pkg" (unpinned!)
)


def is_manifest_path(path: str) -> bool:
    if not path:
        return False
    p = path.replace("\\", "/").lower()
    if any(frag.replace("\\", "/").lower() in p for frag in MANIFEST_PATH_FRAGMENTS):
        return True
    name = p.rsplit("/", 1)[-1]
    return bool(MANIFEST_NAME_RE.search(name))


def find_added_dependency_lines(edits: list[dict[str, Any]]) -> list[str]:
    """Return new_string lines that look like dependency declarations."""
    found: list[str] = []
    for edit in edits or []:
        new_string = edit.get("new_string") or ""
        old_string = edit.get("old_string") or ""
        # Only consider lines present in new_string but not in old_string.
        old_lines = set(old_string.splitlines())
        for line in new_string.splitlines():
            if line in old_lines:
                continue
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if any(pat.search(line) for pat in DEP_HINT_PATTERNS):
                found.append(stripped)
    return found


# --- hook responses ---------------------------------------------------------

SHELL_AGENT_MESSAGE = (
    "Dependency install detected ({label}). The trading-lab repo follows "
    "`.cursor/rules/library-research.mdc`: before adding any third-party "
    "package, search the web for current docs, breaking-change notes, and "
    "version compatibility against `pyproject.toml` `requires-python` (and "
    "`package.json` engines, if relevant).\n\n"
    "Packages: {packages}\n\n"
    "Required actions before approving:\n"
    "  1. `WebSearch <pkg> docs` and `WebSearch <pkg> changelog <year>`.\n"
    "  2. Pin a known-compatible version (no unpinned ranges).\n"
    "  3. Cite the URL(s) consulted in your response / SESSION_LOG entry.\n"
    "  4. Confirm the package isn't redundant with one already in "
    "`pyproject.toml` or `package.json`.\n\n"
    "If you have already done this research in the current turn and cited "
    "your sources, the user can approve. Otherwise, do the research first "
    "and re-issue the install command."
)

SHELL_USER_MESSAGE = (
    "Hook flagged a dependency install ({label}: {packages}). Approve only "
    "if the agent has cited the docs / changelog it consulted and pinned a "
    "specific version."
)

EDIT_AGENT_MESSAGE = (
    "Edit to {file_path} added what looks like {n} dependency line(s):\n"
    "{lines}\n\n"
    "Per `.cursor/rules/library-research.mdc`, every added or upgraded "
    "dependency requires evidence of web research (docs URL, version "
    "compatibility against `requires-python` / engines, changelog review). "
    "Cite that evidence in the SESSION_LOG entry for this change. If the "
    "edit was a rename or rearrangement (no new package), say so explicitly."
)


def _handle_before_shell(payload: dict[str, Any]) -> None:
    command = str(payload.get("command", "") or "")
    if not command:
        allow()
        return

    is_install, label, packages = classify_command(command)
    if not is_install:
        allow()
        return

    pkg_str = ", ".join(packages)
    ask(
        user_message=SHELL_USER_MESSAGE.format(label=label, packages=pkg_str),
        agent_message=SHELL_AGENT_MESSAGE.format(label=label, packages=pkg_str),
    )


def _handle_after_edit(payload: dict[str, Any]) -> None:
    file_path = str(payload.get("file_path", "") or "")
    if not is_manifest_path(file_path):
        write_output({})
        return

    edits = payload.get("edits") or []
    added = find_added_dependency_lines(edits)
    if not added:
        write_output({})
        return

    ensure_state()
    record = {
        "ts": now_iso(),
        "event": "afterFileEdit",
        "file_path": file_path,
        "added_lines": added,
        "conversation_id": payload.get("conversation_id"),
        "generation_id": payload.get("generation_id"),
    }
    append_jsonl(STATE_DIR / "dependency-touches.jsonl", record)

    formatted_lines = "\n".join(
        f"  - {line}" for line in added[:MAX_LINES_IN_AGENT_MESSAGE]
    )
    if len(added) > MAX_LINES_IN_AGENT_MESSAGE:
        formatted_lines += (
            f"\n  ... and {len(added) - MAX_LINES_IN_AGENT_MESSAGE} more"
        )
    write_output(
        {
            "agent_message": EDIT_AGENT_MESSAGE.format(
                file_path=file_path,
                n=len(added),
                lines=formatted_lines,
            ),
        }
    )


def run_hook() -> None:
    payload = read_input()
    if not isinstance(payload, dict):
        allow()
        return

    event = str(payload.get("hook_event_name") or "")
    if event == "afterFileEdit":
        _handle_after_edit(payload)
    elif event == "beforeShellExecution":
        _handle_before_shell(payload)
    elif "command" in payload:
        # Some Cursor versions omit hook_event_name on beforeShellExecution.
        _handle_before_shell(payload)
    elif "file_path" in payload and "edits" in payload:
        _handle_after_edit(payload)
    else:
        # Unknown shape — fail open.
        allow()


# --- self-test --------------------------------------------------------------

SHELL_CASES: list[tuple[str, bool, list[str], str]] = [
    # (command, expect_install, expected_packages_subset, note)
    ("pip install requests", True, ["requests"], "basic pip install"),
    ("pip3 install httpx tenacity", True, ["httpx", "tenacity"], "multiple packages"),
    (
        "python -m pip install --upgrade pandas",
        True,
        ["pandas"],
        "python -m pip with flag",
    ),
    ("uv add ruff", True, ["ruff"], "uv add"),
    ("uv pip install mypy==1.10.0", True, ["mypy==1.10.0"], "uv pip install pinned"),
    ("poetry add lightgbm", True, ["lightgbm"], "poetry add"),
    ("npm install react", True, ["react"], "npm install"),
    ("npm i lodash", True, ["lodash"], "npm i"),
    ("yarn add @tanstack/react-query", True, ["@tanstack/react-query"], "scoped pkg"),
    ("pnpm add zod", True, ["zod"], "pnpm add"),
    ("conda install -c conda-forge polars", True, ["polars"], "conda install"),
    # Negative cases
    ("pip install -e .", False, [], "editable install of current project"),
    ("pip install -r requirements.txt", False, [], "install from file"),
    ("npm install", False, [], "npm install with no args"),
    ("yarn install", False, [], "yarn install with no args"),
    ("pip --version", False, [], "version probe"),
    ("git pip install --help", False, [], "pip not at start"),
    ("ruff check .", False, [], "non-install tool"),
    ("python -m pytest -q", False, [], "test runner"),
    ("echo 'pip install foo'", False, [], "just an echo of the command"),
    ("python scripts/install.py", False, [], "script named install"),
]


MANIFEST_CASES: list[tuple[str, list[dict[str, str]], list[str], str]] = [
    (
        "/repo/pyproject.toml",
        [
            {
                "old_string": '"pandas>=2.0",\n',
                "new_string": '"pandas>=2.0",\n"requests==2.32.0",\n',
            }
        ],
        ['"requests==2.32.0",'],
        "pep621 added pinned dep",
    ),
    (
        "/repo/requirements.txt",
        [
            {
                "old_string": "duckdb==1.0.0\n",
                "new_string": "duckdb==1.0.0\nhttpx==0.27.0\n",
            }
        ],
        ["httpx==0.27.0"],
        "requirements.txt new line",
    ),
    (
        "/repo/frontend/package.json",
        [
            {
                "old_string": '    "next": "14.2.0"\n',
                "new_string": '    "next": "14.2.0",\n    "zod": "^3.23.0"\n',
            }
        ],
        ['"zod": "^3.23.0"'],
        "package.json new dep",
    ),
    (
        "/repo/README.md",
        [{"old_string": "x", "new_string": '"foo": "1.0"'}],
        [],
        "non-manifest file is ignored even with deplike content",
    ),
    (
        "/repo/pyproject.toml",
        [
            {
                "old_string": "name = 'old'",
                "new_string": "name = 'old'\n# just a comment",
            }
        ],
        [],
        "comment-only edit",
    ),
]


def _check_shell_case(
    command: str, expect_install: bool, expected_pkgs: list[str], note: str
) -> str | None:
    """Return a failure message or None if the case passed."""
    is_install, label, packages = classify_command(command)
    ok = is_install == expect_install
    if ok and expect_install:
        ok = all(expected in packages for expected in expected_pkgs)
    if ok:
        return None
    return (
        f"  [FAIL shell] {note!r}\n"
        f"            expected install={expect_install} pkgs⊇{expected_pkgs}\n"
        f"            got      install={is_install} pkgs={packages} "
        f"label={label!r}\n"
        f"            command={command!r}"
    )


def _check_manifest_case(
    file_path: str,
    edits: list[dict[str, str]],
    expected_added_subset: list[str],
    note: str,
) -> str | None:
    """Return a failure message or None if the case passed."""
    manifest_match = is_manifest_path(file_path)
    added = find_added_dependency_lines(edits) if manifest_match else []
    if expected_added_subset:
        ok = manifest_match and all(
            any(expected in line for line in added)
            for expected in expected_added_subset
        )
    else:
        ok = not added
    if ok:
        return None
    return (
        f"  [FAIL edit ] {note!r}\n"
        f"            file_path={file_path!r} manifest={manifest_match}\n"
        f"            expected added⊇{expected_added_subset}\n"
        f"            got      added={added}"
    )


def run_self_test(
    shell_cases: Iterable[tuple[str, bool, list[str], str]] = SHELL_CASES,
    manifest_cases: Iterable[
        tuple[str, list[dict[str, str]], list[str], str]
    ] = MANIFEST_CASES,
) -> int:
    failures: list[str] = []
    total = 0

    for command, expect_install, expected_pkgs, note in shell_cases:
        total += 1
        failure = _check_shell_case(command, expect_install, expected_pkgs, note)
        if failure is None:
            sys.stdout.write(f"  [ok shell]   {note}\n")
        else:
            failures.append(failure)

    for file_path, edits, expected_added_subset, note in manifest_cases:
        total += 1
        failure = _check_manifest_case(
            file_path, edits, expected_added_subset, note
        )
        if failure is None:
            sys.stdout.write(f"  [ok edit]    {note}\n")
        else:
            failures.append(failure)

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
        help="Run internal classification cases instead of reading stdin.",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return run_self_test()

    try:
        run_hook()
    except Exception as exc:
        sys.stderr.write(f"check_dependency_research hook error: {exc}\n")
        # Fall back to allow / no-op so we never block on our own bug.
        try:
            allow()
        except Exception:
            write_output({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
