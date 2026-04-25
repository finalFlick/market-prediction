"""Per `.cursor/rules/security.mdc`: there must be no risk-bypass code path.

This test checks two invariants:

1. The `RiskEngine.check_and_size` method is the only public entry point
   used by the backtest engine and the brokers (i.e. neither calls
   `place_order` without going through `check_and_size` first).
2. There is no flag or environment variable that lets a caller skip risk.

The check is heuristic — it scans source for forbidden patterns. Adding
real bypass logic will require deleting this test, which makes the
intention explicit during code review.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]

_FORBIDDEN_FLAGS = (
    "skip_risk",
    "bypass_risk",
    "no_risk_check",
    "RISK_BYPASS",
    "DISABLE_RISK",
)
_FORBIDDEN_TODO = re.compile(r"#\s*(TODO|FIXME)[^\n]*?(skip|disable|bypass)\s*risk", re.IGNORECASE)


@pytest.mark.security
def test_no_risk_bypass_flags_in_repo() -> None:
    offenders: list[str] = []
    for path in _ROOT.rglob("*.py"):
        rel = path.relative_to(_ROOT).as_posix()
        if rel.startswith(("tests/", "ai_evals/", ".cursor/")):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for flag in _FORBIDDEN_FLAGS:
            if flag in text:
                offenders.append(f"{rel} :: {flag}")
        if _FORBIDDEN_TODO.search(text):
            offenders.append(f"{rel} :: TODO/FIXME suggesting risk bypass")
    assert not offenders, "risk-bypass markers found: " + "; ".join(offenders)
