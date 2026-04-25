---
name: script-first-python
description: Persist generated Python as a reusable file under scripts/ instead of running it inline. Use whenever the agent is about to write Python via python -c, a heredoc piped into python, an inline notebook-style snippet, or any one-off script that takes more than a single trivial expression. The companion beforeShellExecution hook (.cursor/hooks/no_inline_python.py) flags violations.
---

# script-first-python

The trading-lab repo treats generated Python as a durable artifact. Every
non-trivial snippet the agent would otherwise run inline is written to a
file, indexed in `SCRIPTS.md`, and reused on the next session.

The goal: **generate a script once. Edit it later. Never re-derive it.**

## When to use

Apply this skill whenever the agent is about to:

- run `python -c "..."` or `python3 -c "..."`
- pipe a multi-line snippet into `python` via heredoc, `echo`, or
  `Get-Content`
- author "throwaway" Python that computes something the user might ask
  again later (probe data, dump a table, sanity-check a parquet file,
  compare two manifests, render a quick chart, etc.)
- repeat a pattern from a previous session that ended up as inline code

The companion hook `.cursor/hooks/no_inline_python.py` will surface a
warning if you try to bypass this skill via `beforeShellExecution`.

## Procedure

### 1. Search first — never regenerate

Before writing any new Python, look for an existing script that already
does it.

```bash
rg -l "<keywords>" scripts/ .cursor/scripts/ 2>/dev/null
```

Also scan `SCRIPTS.md` (the index) for matching descriptions.

If a script already exists: invoke it with the right CLI flags and
**stop**. Edit it only if the existing behavior is wrong or insufficient.

### 2. Pick the right home

| Purpose                                     | Location                             |
| ------------------------------------------- | ------------------------------------ |
| Operational / one-shot CLIs the user runs   | `scripts/<verb>-<noun>.py`           |
| Repo maintenance, hooks, dev tooling        | `.cursor/scripts/<verb>-<noun>.py`   |
| Logic re-used by production code            | proper module under `data/`, `research/`, `risk/`, etc. (not `scripts/`) |

Use kebab-case file names: `dump-features.py`, `compare-manifests.py`,
`probe-duckdb-schema.py`. Verbs first, nouns second.

`scripts/` is for things a human might invoke from the terminal. If the
code wants to be `import`-able from production modules, it does not
belong in `scripts/` — it belongs in the matching package.

### 3. Standard script skeleton

Every script in `scripts/` follows this shape:

```python
"""<one-line purpose>.

Inputs:
    --<flag>: <what it expects>

Outputs:
    <stdout shape OR file path written>

Example:
    python scripts/<name>.py --<flag> <value>
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--example", required=True)
    args = parser.parse_args(argv)
    # ... do the work ...
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Required:

- Module docstring with **purpose, inputs, outputs, example invocation**.
- `argparse` for every input. No hardcoded paths or dates.
- `if __name__ == "__main__":` guard so the file is import-safe.
- Return an integer exit code (`0` = success, non-zero = failure).
- No side effects on import.

### 4. Update the catalog

After saving the script, append one row to `SCRIPTS.md`:

```markdown
| script | purpose | example |
| --- | --- | --- |
| `scripts/dump-features.py` | dump features.parquet head + dtypes | `python scripts/dump-features.py --rows 20` |
```

Keep entries alphabetical by filename. The catalog is the discovery
surface for future sessions — without it, the skill's "search first"
step degrades into reading every file under `scripts/`.

### 5. Promote to a skill once stable

If you run the same script in **three or more sessions**, or it embeds
non-trivial workflow steps that benefit from being explained in prose,
promote it to a skill:

1. Create `.cursor/skills/<skill-name>/SKILL.md` using
   `C:\Users\Brandon\.cursor\skills-cursor\create-skill\SKILL.md` as the
   template.
2. Move the script into the skill folder
   (`.cursor/skills/<skill-name>/scripts/<name>.py`) **only** if it is
   exclusively used by that skill. Otherwise leave it in `scripts/` and
   reference it from the SKILL.md.
3. Add a row in `SCRIPTS.md` noting the script was promoted, with a
   pointer to the skill.

Promotion captures the *workflow* (when, why, how to interpret outputs);
the script captures the *mechanics*.

## Forbidden

- `python -c "..."` for anything beyond a single short expression.
- Heredocs piped into `python` (`python <<EOF ... EOF`,
  `@"..."@ | python`).
- Generating the same logic in two different sessions instead of
  reusing the existing script.
- Saving scripts under random names (`tmp.py`, `script1.py`, `test.py`).
- Committing scripts without an entry in `SCRIPTS.md`.
- Putting `import`-able production logic in `scripts/`. The pipeline
  hierarchy in `.cursor/rules/architecture.mdc` still applies.

## Allowed inline exceptions

The following are short enough to remain inline and do not need a script:

- `python --version`, `python -m pip list`, `python -m pytest -q`
- `python -m <module> [--flags]` invocations (running an existing module)
- Single-expression probes the user explicitly asks for once, e.g.
  `python -c "import sys; print(sys.executable)"`. The hook will return
  `permission: "ask"` for these so the user can approve case-by-case.

When in doubt: **write the file**. Disk is cheap; regeneration is not.
