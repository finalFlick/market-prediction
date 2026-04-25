"""Common Model protocol implemented by every backbone."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import numpy as np
import pandas as pd


class Model(Protocol):
    """Minimal contract: fit, predict, save, load."""

    name: str

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None: ...

    def predict(self, X: pd.DataFrame) -> np.ndarray: ...

    def save(self, path: str | Path) -> None: ...

    @classmethod
    def load(cls, path: str | Path) -> Model: ...
