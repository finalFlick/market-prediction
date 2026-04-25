"""Persistence for `RiskDecision` rows. MVP-0: in-memory; §E adds DuckDB + hash chain."""

from __future__ import annotations

from risk.audit import InMemoryRiskAudit, RiskAudit, RiskDecision


class RiskDecisionsRepository:
    """Thin wrapper so orchestration can swap storage without touching RiskEngine callbacks."""

    def __init__(self, *, audit: RiskAudit | None = None) -> None:
        self._inner = audit if audit is not None else InMemoryRiskAudit()

    @property
    def sink(self) -> RiskAudit:
        return self._inner

    def record(self, d: RiskDecision) -> None:
        self._inner.emit(d)

    @property
    def decisions(self) -> list[RiskDecision]:
        if isinstance(self._inner, InMemoryRiskAudit):
            return list(self._inner.items)
        return []
