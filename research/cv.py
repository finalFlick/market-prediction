"""Time-series cross-validation: walk-forward and purged k-fold with embargo.

Embargo prevents label leakage when a label at time `t` looks `h` bars into
the future: the validation fold cannot include any sample whose label
overlaps the training fold.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Fold:
    train_idx: np.ndarray
    valid_idx: np.ndarray


def walk_forward(n_samples: int, *, n_splits: int, embargo: int = 0) -> Iterator[Fold]:
    """Expanding-window walk-forward folds.

    With `n_splits=5` and `n_samples=1000`, validation windows are roughly
    [200,400), [400,600), [600,800), [800,1000). Each train window is
    everything strictly before the validation window, minus the embargo.
    """
    if n_splits < 2:
        raise ValueError("n_splits must be >= 2")
    if n_samples < n_splits + 1:
        raise ValueError("n_samples must exceed n_splits")
    fold_size = n_samples // (n_splits + 1)
    for k in range(1, n_splits + 1):
        valid_start = (k + 1) * fold_size if k < n_splits else n_samples - fold_size
        valid_end = valid_start + fold_size
        train_end = max(0, valid_start - embargo)
        if train_end <= 0 or valid_end <= valid_start:
            continue
        train_idx = np.arange(0, train_end)
        valid_idx = np.arange(valid_start, min(valid_end, n_samples))
        yield Fold(train_idx=train_idx, valid_idx=valid_idx)


def purged_kfold(
    n_samples: int,
    *,
    n_splits: int,
    label_horizon: int,
    embargo: int = 0,
) -> Iterator[Fold]:
    """Purged k-fold (López de Prado): purge `label_horizon` overlap, then embargo."""
    if n_splits < 2:
        raise ValueError("n_splits must be >= 2")
    indices = np.arange(n_samples)
    fold_size = n_samples // n_splits
    purge = label_horizon
    for k in range(n_splits):
        v_start = k * fold_size
        v_end = (k + 1) * fold_size if k < n_splits - 1 else n_samples
        valid_idx = indices[v_start:v_end]
        # Purge a window around the validation block; apply embargo on the right.
        mask = np.ones(n_samples, dtype=bool)
        mask[max(0, v_start - purge) : min(n_samples, v_end + purge + embargo)] = False
        train_idx = indices[mask]
        if train_idx.size == 0 or valid_idx.size == 0:
            continue
        yield Fold(train_idx=train_idx, valid_idx=valid_idx)
