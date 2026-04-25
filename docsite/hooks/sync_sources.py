"""Copy repo markdown sources into docsite/ before MkDocs build (ephemeral, not in git)."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

# Root-level .md to mirror into docsite/ (keep in sync with plan).
ROOT_MDS: tuple[str, ...] = (
    "AGENTS.md",
    "CHANGELOG.md",
    "DECISIONS.md",
    "PROJECT_CONTEXT.md",
    "RUNNING.md",
    "SIGNALS.md",
    "TODO.md",
    "WORKFLOW.md",
)

# Folders to mirror.
COPY_TREES: tuple[str, ...] = (
    "specs",
    "docs",
)


def on_config(config: Any, **kwargs: Any) -> Any:
    root = Path(config["config_file_path"]).resolve().parent
    site = root / "docsite"

    for name in COPY_TREES:
        src = root / name
        dst = site / name
        if not src.is_dir():
            continue
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, dirs_exist_ok=True)

    for filename in ROOT_MDS:
        src = root / filename
        dst = site / filename
        if not src.is_file():
            if dst.is_file():
                dst.unlink()
            continue
        shutil.copy2(src, dst)

    return config
