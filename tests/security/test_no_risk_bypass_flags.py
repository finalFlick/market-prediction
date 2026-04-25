"""Forbidden risk-bypass strings must not appear in application code (security.mdc)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORBIDDEN = (
    "skip_risk",
    "bypass_risk",
    "RISK_BYPASS",
    "DISABLE_RISK",
    "--no-risk",
)
# Application packages only (excludes tests, docs, specs, DECISIONS, etc.) per risk-management.mdc.
APP_ROOTS = (
    "data",
    "research",
    "strategies",
    "risk",
    "backtests",
    "execution",
    "monitoring",
    "backend",
    "runs",
    "learning",
)
CODE_SUFFIXES = (".py",)


def _should_scan(path: Path, rel: str) -> bool:
    r = rel.replace("\\", "/")
    if "test_no_risk_bypass_flags" in r:
        return False
    if "backtests/results/" in r:
        return False
    return path.suffix == ".py"


def test_no_bypass_phrases_in_production_code() -> None:
    hits: list[str] = []
    for sub in APP_ROOTS:
        base = ROOT / sub
        if not base.is_dir():
            continue
        for path in base.rglob("*.py"):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            if not _should_scan(path, rel):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for phrase in FORBIDDEN:
                if phrase in text:
                    hits.append(f"{rel}: contains {phrase!r}")
    assert not hits, "forbidden risk bypass tokens:\n" + "\n".join(hits)
