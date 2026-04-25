"""Simple PyTorch MLP regressor — a placeholder for sequence models.

Replace with an LSTM / TCN / transformer when sequence features land. The
public surface (fit/predict/save/load) is the same as the tabular models so
strategies don't care which backbone is in use.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from monitoring.logger import get_logger

log = get_logger(__name__)


class _MLP(nn.Module):
    def __init__(self, in_dim: int, hidden: int = 128, dropout: float = 0.1) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return cast(torch.Tensor, self.net(x).squeeze(-1))


class TorchMLPRegressor:
    name = "torch_mlp"

    def __init__(
        self,
        *,
        hidden: int = 128,
        dropout: float = 0.1,
        epochs: int = 20,
        batch_size: int = 4096,
        lr: float = 1e-3,
        seed: int = 42,
        device: str = "cpu",
        **_: Any,
    ) -> None:
        self.hidden = hidden
        self.dropout = dropout
        self.epochs = epochs
        self.batch_size = batch_size
        self.lr = lr
        self.seed = seed
        self.device = torch.device(device)
        self._model: _MLP | None = None
        self._feature_names: list[str] | None = None
        self._mean: np.ndarray | None = None
        self._std: np.ndarray | None = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        torch.manual_seed(self.seed)
        np.random.seed(self.seed)

        self._feature_names = list(X.columns)
        x_arr = X.to_numpy(dtype=np.float32)
        self._mean = x_arr.mean(axis=0)
        self._std = x_arr.std(axis=0) + 1e-8
        x_arr = (x_arr - self._mean) / self._std
        y_arr = y.to_numpy(dtype=np.float32)

        ds = TensorDataset(torch.from_numpy(x_arr), torch.from_numpy(y_arr))
        loader = DataLoader(ds, batch_size=self.batch_size, shuffle=True, drop_last=False)

        model = _MLP(in_dim=x_arr.shape[1], hidden=self.hidden, dropout=self.dropout).to(
            self.device
        )
        opt = torch.optim.Adam(model.parameters(), lr=self.lr)
        loss_fn = nn.MSELoss()

        model.train()
        for epoch in range(self.epochs):
            total = 0.0
            for xb_batch, yb_batch in loader:
                xb = xb_batch.to(self.device)
                yb = yb_batch.to(self.device)
                opt.zero_grad()
                pred = model(xb)
                loss = loss_fn(pred, yb)
                loss.backward()
                opt.step()
                total += float(loss.detach()) * xb.shape[0]
            log.info("torch_mlp.epoch", epoch=epoch, loss=total / len(ds))
        self._model = model

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if self._model is None or self._feature_names is None:
            raise RuntimeError("model is not fitted")
        assert self._mean is not None and self._std is not None
        x_arr = (X[self._feature_names].to_numpy(dtype=np.float32) - self._mean) / self._std
        self._model.eval()
        with torch.no_grad():
            out = self._model(torch.from_numpy(x_arr).to(self.device)).cpu().numpy()
        return np.asarray(out)

    def save(self, path: str | Path) -> None:
        if self._model is None:
            raise RuntimeError("model is not fitted")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "state_dict": self._model.state_dict(),
                "feature_names": self._feature_names,
                "mean": self._mean,
                "std": self._std,
                "hidden": self.hidden,
                "dropout": self.dropout,
            },
            path,
        )

    @classmethod
    def load(cls, path: str | Path) -> TorchMLPRegressor:
        ckpt = torch.load(str(path), map_location="cpu")
        m = cls(hidden=ckpt["hidden"], dropout=ckpt["dropout"])
        m._feature_names = ckpt["feature_names"]
        m._mean = ckpt["mean"]
        m._std = ckpt["std"]
        model = _MLP(
            in_dim=len(ckpt["feature_names"]),
            hidden=ckpt["hidden"],
            dropout=ckpt["dropout"],
        )
        model.load_state_dict(ckpt["state_dict"])
        m._model = model
        return m
