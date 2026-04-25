"""afterFileEdit hook: run `ruff format` on the edited Python file.

Best-effort. If ruff isn't installed or the file isn't Python, this hook
is a no-op. It does not block edits and never returns ``permission: deny``.
"""

from __future__ import annotations

import contextlib
import shutil
import subprocess
import sys

from _common import read_input, write_output


def main() -> None:
    payload = read_input()
    file_path = payload.get("file_path") or ""

    if not file_path.endswith(".py"):
        write_output({})
        return

    ruff = shutil.which("ruff")
    if ruff is None:
        write_output({})
        return

    with contextlib.suppress(subprocess.SubprocessError, OSError):
        subprocess.run(
            [ruff, "format", "--quiet", file_path],
            check=False,
            timeout=10,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    write_output({})


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write(f"format_python hook error: {exc}\n")
        write_output({})
