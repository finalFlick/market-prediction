"""Persist `RiskDecision` into ``ha_risk_decisions`` (hash chain, §E)."""

from __future__ import annotations

import duckdb

from data.repositories.audit.chain import append_row
from risk.audit import RiskDecision


class DuckDBRiskAudit:
    """`RiskEngine` callback that appends to ``ha_risk_decisions``."""

    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self._conn = conn

    def emit(self, decision: RiskDecision) -> None:
        append_row(
            self._conn,
            "ha_risk_decisions",
            natural_key=decision.decision_id,
            payload=decision.model_dump(mode="json"),
            run_id=decision.run_id,
        )
