"""Cheap secret scan: catch obvious accidental commits.

Heavier scanners (gitleaks) run in CI; this test catches the common cases
during local pytest runs so PRs surface failures before pushing.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]

# Skip large binaries / vendored trees / generated artifacts.
_SKIP_DIRS = {
    "node_modules",
    ".git",
    ".venv",
    "venv",
    ".next",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "data/raw",
    "data/processed",
    "backtests/results",
    "frontend/.next",
}

# Patterns broad enough to catch the obvious mistakes, narrow enough to ignore
# Pydantic field defaults and example strings.
_PATTERNS = {
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "openai_key": re.compile(r"sk-[A-Za-z0-9]{20,}"),
    "private_pem": re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
}


def _iter_files() -> list[Path]:
    out: list[Path] = []
    for p in _ROOT.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(_ROOT).as_posix()
        if any(rel.startswith(skip) or f"/{skip}/" in f"/{rel}/" for skip in _SKIP_DIRS):
            continue
        if p.suffix in {".png", ".jpg", ".jpeg", ".pdf", ".duckdb", ".parquet"}:
            continue
        if p.name in {".env", ".env.local"}:
            pytest.fail(f"committed secret-bearing file: {rel}")
        out.append(p)
    return out


@pytest.mark.security
def test_no_obvious_secrets() -> None:
    offenders: list[str] = []
    for path in _iter_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for name, pat in _PATTERNS.items():
            if pat.search(text):
                offenders.append(f"{path.relative_to(_ROOT)} :: {name}")
    assert not offenders, "secret patterns matched: " + "; ".join(offenders)
