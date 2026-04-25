"""Risk decision audit events (satisfies Req 20, 24; Day-0 audit lineage)."""

from __future__ import annotations

from typing import Any, Literal, Protocol
from uuid import uuid4

from pydantic import BaseModel, Field


class RiskDecision(BaseModel, frozen=True):
    """A single risk-engine decision, suitable for append-only storage and hash chains."""

    decision_id: str
    run_id: str | None
    client_id: str | None
    rule: str
    outcome: Literal["accept", "reject", "skip"]
    message: str
    details: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def new(
        cls,
        *,
        run_id: str | None,
        client_id: str | None,
        rule: str,
        outcome: Literal["accept", "reject", "skip"],
        message: str = "",
        **details: Any,
    ) -> RiskDecision:
        return cls(
            decision_id=str(uuid4()),
            run_id=run_id,
            client_id=client_id,
            rule=rule,
            outcome=outcome,
            message=message,
            details=dict(details) if details else {},
        )


class RiskAudit(Protocol):
    def emit(self, decision: RiskDecision) -> None: ...


class InMemoryRiskAudit:
    """Test / dev sink for risk decisions before DuckDB + hash chain (see §E)."""

    def __init__(self) -> None:
        self.items: list[RiskDecision] = []

    def emit(self, decision: RiskDecision) -> None:
        self.items.append(decision)
