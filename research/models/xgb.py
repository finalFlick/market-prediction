"""XGBoost regressor for predicting forward returns."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb

from monitoring.logger import get_logger

log = get_logger(__name__)


class XGBRegressor:
    """Thin wrapper around xgboost with safe defaults."""

    name = "xgb"

    def __init__(self, **params: Any) -> None:
        defaults: dict[str, Any] = {
            "objective": "reg:squarederror",
            "tree_method": "hist",
            "max_depth": 6,
            "eta": 0.05,
            "subsample": 0.9,
            "colsample_bytree": 0.9,
            "min_child_weight": 5.0,
            "seed": 42,
        }
        defaults.update(params)
        self.params = defaults
        self.num_boost_round = int(params.get("num_boost_round", 500))
        self._booster: xgb.Booster | None = None
        self._feature_names: list[str] | None = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        self._feature_names = list(X.columns)
        dtrain = xgb.DMatrix(X.to_numpy(), label=y.to_numpy(), feature_names=self._feature_names)
        self._booster = xgb.train(self.params, dtrain, num_boost_round=self.num_boost_round)
        log.info("xgb.fit", rows=len(X), features=len(self._feature_names))

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self._booster is None or self._feature_names is None:
            raise RuntimeError("model is not fitted")
        d = xgb.DMatrix(X[self._feature_names].to_numpy(), feature_names=self._feature_names)
        return np.asarray(self._booster.predict(d))

    def save(self, path: str | Path) -> None:
        if self._booster is None:
            raise RuntimeError("model is not fitted")
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._booster.save_model(str(path))

    @classmethod
    def load(cls, path: str | Path) -> XGBRegressor:
        m = cls()
        booster = xgb.Booster()
        booster.load_model(str(path))
        m._booster = booster
        feature_names = booster.feature_names
        m._feature_names = list(feature_names) if feature_names is not None else None
        return m
