"""Model registry: each trained artifact gets an immutable directory + manifest."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _git_commit() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL
        )
        return out.decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _config_hash(config: dict[str, Any]) -> str:
    payload = json.dumps(config, sort_keys=True, default=str).encode()
    return hashlib.sha256(payload).hexdigest()[:12]


class ModelRegistry:
    """Immutable, content-addressable registry rooted at `research/models/registry/`."""

    def __init__(self, root: str | Path = "research/models/registry") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def make_run_dir(self, name: str, config: dict[str, Any]) -> Path:
        ts = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
        commit = _git_commit()
        cfg_hash = _config_hash(config)
        run_id = f"{name}-{ts}-{commit}-{cfg_hash}"
        path = self.root / run_id
        path.mkdir(parents=True, exist_ok=False)
        return path

    @staticmethod
    def write_manifest(run_dir: Path, manifest: dict[str, Any]) -> None:
        manifest = {
            **manifest,
            "git_commit": _git_commit(),
            "created_at": datetime.now(tz=UTC).isoformat(),
        }
        (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
