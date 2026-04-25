"""Manifest writer for backtest runs.

Every run id encodes timestamp + git commit + config hash. Re-running with
the same config and data must produce a byte-identical `metrics.json`.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
        ).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def config_hash(config: dict[str, Any]) -> str:
    payload = json.dumps(config, sort_keys=True, default=str).encode()
    return hashlib.sha256(payload).hexdigest()[:12]


def make_run_dir(root: str | Path, *, name: str, config: dict[str, Any]) -> Path:
    ts = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{name}-{ts}-{git_commit()}-{config_hash(config)}"
    path = Path(root) / run_id
    path.mkdir(parents=True, exist_ok=False)
    return path


def write_manifest(run_dir: Path, *, config: dict[str, Any], extra: dict[str, Any]) -> None:
    manifest = {
        "git_commit": git_commit(),
        "created_at": datetime.now(tz=UTC).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "config": config,
        **extra,
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
