# SCRIPTS.md

Index of reusable Python scripts in this repo. The agent searches this file
**before** writing any new inline Python. See
`.cursor/skills/script-first-python/SKILL.md` for the convention.

A script earns a row here when it:

- Is invokable from the terminal (has `argparse` + `if __name__ == "__main__"`).
- Solves a concrete, repeatable task (probe, dump, compare, render, etc.).
- Lives under `scripts/` (operational) or `.cursor/scripts/` (repo tooling).

If a script is reused in **3+ sessions**, promote it to a skill under
`.cursor/skills/<skill-name>/` and add a `→ promoted` note in this index.

---

## Operational scripts (`scripts/`)

| script | purpose | example |
| --- | --- | --- |
| _(none yet — first inline-Python need will land here)_ | | |

## Repo-tooling scripts (`.cursor/scripts/` and `.cursor/hooks/`)

| script | purpose | example |
| --- | --- | --- |
| `.cursor/hooks/no_inline_python.py` | beforeShellExecution hook that redirects inline Python to a saved script | `python .cursor/hooks/no_inline_python.py --self-test` |
