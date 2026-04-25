"""Frozen run configuration and typed identifiers."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class RunConfig(BaseModel, frozen=True):
    """Snapshot taken at `submit`; never mutated in flight."""

    run_id: str = Field(default_factory=lambda: str(uuid4()))
    run_type: Literal["backtest", "paper", "strategy_test"] = "backtest"
    mode: Literal["backtest", "paper", "live", "dry_run"] = "backtest"
    strategy_dotted: str = "strategies.examples.momentum_xover.MomentumXover"
    backtest_config_path: str | None = "configs/backtest.yaml"
    capital: float = 10_000.0
    seed: int = 42
    trigger_is_ai: bool = False

    def config_hash(self) -> str:
        raw = self.model_dump_json()
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


class RunEvent(BaseModel, frozen=True):
    """Durable outbox + SSE payload."""

    run_id: str
    event_id: str
    kind: str
    ts: datetime
    payload: dict[str, Any] = Field(default_factory=dict)
