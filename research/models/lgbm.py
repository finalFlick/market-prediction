"""LightGBM regressor for predicting forward returns."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np
import pandas as pd

from monitoring.logger import get_logger

log = get_logger(__name__)


class LGBMRegressor:
    """Thin wrapper around lightgbm.LGBMRegressor with safe defaults."""

    name = "lgbm"

    def __init__(self, **params: Any) -> None:
        defaults: dict[str, Any] = {
            "objective": "regression",
            "metric": "rmse",
            "learning_rate": 0.05,
            "num_leaves": 63,
            "min_data_in_leaf": 100,
            "feature_fraction": 0.9,
            "bagging_fraction": 0.9,
            "bagging_freq": 5,
            "num_iterations": 500,
            "seed": 42,
            "deterministic": True,
            "verbosity": -1,
        }
        defaults.update(params)
        self.params = defaults
        self._booster: lgb.Booster | None = None
        self._feature_names: list[str] | None = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        self._feature_names = list(X.columns)
        dtrain = lgb.Dataset(X.to_numpy(), label=y.to_numpy(), feature_name=self._feature_names)
        self._booster = lgb.train(self.params, dtrain)
        log.info("lgbm.fit", rows=len(X), features=len(self._feature_names))

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self._booster is None or self._feature_names is None:
            raise RuntimeError("model is not fitted")
        return np.asarray(self._booster.predict(X[self._feature_names].to_numpy()))

    def save(self, path: str | Path) -> None:
        if self._booster is None:
            raise RuntimeError("model is not fitted")
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._booster.save_model(str(path))

    @classmethod
    def load(cls, path: str | Path) -> LGBMRegressor:
        m = cls()
        m._booster = lgb.Booster(model_file=str(path))
        m._feature_names = m._booster.feature_name()
        return m
