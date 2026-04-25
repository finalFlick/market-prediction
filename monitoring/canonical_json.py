"""Canonical JSON for deterministic artifacts (Day-0 Invariant 3).

Sorted keys, Decimal as string, UTC datetimes with ``Z`` suffix, NaN/Inf
forbidden, bytes as hex.
"""

from __future__ import annotations

import json
import math
from datetime import UTC, date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Any


class NonFiniteFloatError(ValueError):
    """Raised when a float is NaN or infinite."""


def _to_canonical(obj: Any) -> Any:  # noqa: PLR0911, PLR0912
    if obj is None or isinstance(obj, bool):
        return obj
    if isinstance(obj, str):
        return obj
    if isinstance(obj, int) and not isinstance(obj, bool):
        return obj
    if isinstance(obj, float):
        if not math.isfinite(obj):
            raise NonFiniteFloatError(f"non-finite float: {obj!r}")
        return obj
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, (bytes, bytearray, memoryview)):
        return bytes(obj).hex()
    if isinstance(obj, datetime):
        if obj.tzinfo is None:
            msg = f"datetime must be tz-aware, got {obj!r}"
            raise ValueError(msg)
        u = obj.astimezone(UTC)
        s = u.strftime("%Y-%m-%dT%H:%M:%S")
        if u.microsecond:
            s += f".{u.microsecond:06d}"
        s += "Z"
        return s
    if isinstance(obj, date) and not isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, time):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {str(k): _to_canonical(v) for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))}
    if isinstance(obj, (list, tuple)):
        return [_to_canonical(x) for x in obj]
    msg = f"unsupported type for canonical JSON: {type(obj).__name__}"
    raise TypeError(msg)


def canonical_dumps(obj: Any) -> str:
    """Return minified canonical JSON (no trailing newline; add in writer if needed)."""
    body = _to_canonical(obj)
    return json.dumps(
        body,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def write_canonical_json(path: str | Path, obj: Any) -> None:
    """Write ``obj`` as a POSIX text file ending in newline."""
    p = Path(path)
    p.write_text(canonical_dumps(obj) + "\n", encoding="utf-8")
