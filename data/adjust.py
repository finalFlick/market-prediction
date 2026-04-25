"""Bar adjustment helpers (crypto: identity; v1+ equities: splits/divs)."""

from __future__ import annotations

import pandas as pd


def pass_through_crypto(df: pd.DataFrame) -> pd.DataFrame:
    """MVP-0: spot crypto has no split adjustments; return a copy for API stability."""
    return df.copy()
