"""CLI: train a signal model from a YAML config and register the artifact."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import click
import numpy as np
import pandas as pd
import yaml

from monitoring.logger import get_logger
from research.cv import walk_forward
from research.labels import forward_log_return
from research.models.base import Model
from research.models.lgbm import LGBMRegressor
from research.models.registry import ModelRegistry
from research.models.torch_mlp import TorchMLPRegressor
from research.models.xgb import XGBRegressor

log = get_logger(__name__)

_BACKBONES: dict[str, type[Model]] = {
    "lgbm": LGBMRegressor,
    "xgb": XGBRegressor,
    "torch_mlp": TorchMLPRegressor,
}


def _load_config(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text())
    return cast(dict[str, Any], raw)


def _build_xy(features_path: Path, horizon: int) -> tuple[pd.DataFrame, pd.Series]:
    features = pd.read_parquet(features_path)
    if not isinstance(features.index, pd.DatetimeIndex):
        raise ValueError("features parquet must be indexed by timestamp")
    if "close" not in features.columns:
        raise ValueError(
            "features parquet must include a 'close' column for label construction; "
            "join close back into the feature matrix in research.features.build"
        )
    y = forward_log_return(features["close"], horizon=horizon)
    X = features.drop(columns=["close"])
    aligned = pd.concat([X, y], axis=1).dropna()
    return aligned.iloc[:, :-1], aligned.iloc[:, -1]


@click.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
)
def main(config_path: Path) -> None:
    """Train a model. The config YAML drives data, label, model, and CV choices."""
    cfg = _load_config(config_path)
    backbone_name = cfg["model"]["backbone"]
    if backbone_name not in _BACKBONES:
        raise click.ClickException(f"unknown backbone '{backbone_name}'")

    features_path = Path(cfg["data"]["features_path"])
    horizon = int(cfg["label"]["horizon"])
    X, y = _build_xy(features_path, horizon=horizon)

    cv_cfg = cfg.get("cv", {"n_splits": 5, "embargo": horizon})
    folds = list(walk_forward(len(X), n_splits=cv_cfg["n_splits"], embargo=cv_cfg["embargo"]))

    backbone_cls = _BACKBONES[backbone_name]
    fold_metrics: list[dict[str, float]] = []
    for i, fold in enumerate(folds):
        model = backbone_cls(**cfg["model"].get("params", {}))
        model.fit(X.iloc[fold.train_idx], y.iloc[fold.train_idx])
        pred = model.predict(X.iloc[fold.valid_idx])
        actual = y.iloc[fold.valid_idx].to_numpy()
        ic = float(np.corrcoef(pred, actual)[0, 1]) if pred.std() > 0 else 0.0
        rmse = float(np.sqrt(((pred - actual) ** 2).mean()))
        log.info("cv.fold", fold=i, ic=ic, rmse=rmse)
        fold_metrics.append({"ic": ic, "rmse": rmse})

    final = backbone_cls(**cfg["model"].get("params", {}))
    final.fit(X, y)

    registry = ModelRegistry()
    run_dir = registry.make_run_dir(name=backbone_name, config=cfg)
    final.save(run_dir / "model.bin")
    registry.write_manifest(
        run_dir,
        {
            "backbone": backbone_name,
            "config_path": str(config_path),
            "config": cfg,
            "n_samples": len(X),
            "n_features": X.shape[1],
            "horizon": horizon,
            "cv_metrics": fold_metrics,
            "mean_ic": float(np.mean([m["ic"] for m in fold_metrics])),
        },
    )
    log.info("train.done", run_dir=str(run_dir))


if __name__ == "__main__":
    main()
