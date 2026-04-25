"""Risk limit configuration loaded from `configs/risk.yaml`."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class RiskLimits(BaseModel):
    """Hard limits enforced by `risk.engine.RiskEngine`."""

    max_gross_exposure: float = Field(1.0, gt=0, description="Gross / equity")
    max_net_exposure: float = Field(1.0, ge=0, description="|Net| / equity")
    max_per_symbol_weight: float = Field(0.5, gt=0, le=1.0)
    max_leverage: float = Field(1.0, gt=0)
    max_daily_loss_pct: float = Field(0.03, gt=0, le=1.0, description="Stop trading at -X equity")
    max_drawdown_pct: float = Field(0.20, gt=0, le=1.0, description="Halt below HWM-X")
    min_order_notional: float = Field(10.0, ge=0)
    target_annual_vol: float = Field(0.15, gt=0, description="Vol target for sizing")
    kill_switch: bool = Field(False, description="If true, reject every order")

    @classmethod
    def from_yaml(cls, path: str | Path) -> RiskLimits:
        return cls.model_validate(yaml.safe_load(Path(path).read_text()))
