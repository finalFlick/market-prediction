"""Inv-7 guard: only runs/events/bus.py may access redis.Redis or xadd directly.

Any other module under runs/ or execution/ that imports redis or calls xadd
bypasses the DuckDB outbox, violating Day-0 Invariant 7.
"""

from __future__ import annotations

import ast
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_ALLOWED = {
    _ROOT / "runs" / "events" / "bus.py",
    _ROOT / "runs" / "events" / "redis_bus.py",  # legacy adapter — allowed to hold the impl
    _ROOT / "runs" / "events" / "factory.py",  # factory selects transport
}
_SCAN_ROOTS = (
    _ROOT / "runs",
    _ROOT / "execution",
)


def _file_uses_redis_directly(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        # `import redis` or `from redis import ...`
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "redis" or alias.name.startswith("redis."):
                    return True
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").startswith("redis"):
                return True
        # direct .xadd( attribute calls
        elif isinstance(node, ast.Attribute) and node.attr == "xadd":
            return True
    return False


def test_no_direct_redis_use_outside_allowed_modules() -> None:
    offenders: list[str] = []
    for root in _SCAN_ROOTS:
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if path in _ALLOWED:
                continue
            if _file_uses_redis_directly(path):
                offenders.append(str(path.relative_to(_ROOT)))
    assert not offenders, (
        "Direct Redis access found outside allowed modules "
        "(use runs.events.bus.publish_event instead):\n" + "\n".join(offenders)
    )
