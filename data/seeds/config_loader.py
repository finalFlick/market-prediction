"""Load `configs/*.yaml` into `config_kv` (MVP-0 read model; v1 adds approval UX)."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml

from data.db import connect, default_path


def _fingerprint(payload: object) -> str:
    s = yaml.safe_dump(
        cast("Any", payload),
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=True,
    )
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def seed_config_kv(
    config_dir: str | Path = Path("configs"),
    *,
    db_path: str | Path | None = None,
) -> int:
    root = Path(config_dir)
    if not root.is_dir():
        return 0
    p = default_path() if db_path is None else Path(db_path)
    conn = connect(p)
    n = 0
    ts = datetime.now(tz=UTC)
    for path in sorted(root.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        fp = _fingerprint(data)
        rec = {
            "path": path.as_posix(),
            "fingerprint_16": fp,
        }
        value_json = json.dumps(rec, sort_keys=True, separators=(",", ":"))
        conn.execute(
            """
            INSERT OR REPLACE INTO config_kv (scope, key, value_json, updated_at)
            VALUES ('file', ?, ?, ?)
            """,
            [path.name, value_json, ts],
        )
        n += 1
    conn.close()
    return n
