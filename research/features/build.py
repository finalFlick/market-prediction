"""CLI: build the canonical feature matrix and write it to parquet."""

from __future__ import annotations

from pathlib import Path

import click
import pandas as pd

from data.store import OHLCVStore
from data.types import Exchange, Timeframe
from monitoring.logger import get_logger
from research.features import momentum, price, volume
from research.features.validation import assert_utc_index

log = get_logger(__name__)


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the canonical feature set. Order matters only for column layout."""
    assert_utc_index(df)
    parts: list[pd.Series | pd.DataFrame] = [
        price.log_returns(df),
        price.realized_vol(df, window=24),
        price.zscore_close(df, window=96),
        volume.dollar_volume(df),
        volume.volume_zscore(df, window=96),
        volume.obv(df),
        momentum.ema_crossover(df, fast=12, slow=26),
        momentum.rsi(df, window=14),
        momentum.macd(df, fast=12, slow=26, signal=9),
    ]
    features = pd.concat(parts, axis=1)
    out = pd.concat([df[["close"]], features], axis=1)
    return out.dropna(how="all")


@click.command()
@click.option("--exchange", type=click.Choice([e.value for e in Exchange]), required=True)
@click.option("--symbol", required=True)
@click.option(
    "--timeframe",
    type=click.Choice([t.value for t in Timeframe]),
    default=Timeframe.H1.value,
)
@click.option("--output", type=click.Path(), default="data/processed/features.parquet")
def main(exchange: str, symbol: str, timeframe: str, output: str) -> None:
    """Read bars for SYMBOL from the store and write the feature matrix."""
    with OHLCVStore() as store:
        df = store.read(Exchange(exchange), symbol, Timeframe(timeframe))
    if df.empty:
        raise click.ClickException(
            f"no bars in store for {exchange}/{symbol}/{timeframe}; run data.ingest.run first"
        )

    features = build_feature_matrix(df)
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_parquet(out_path)
    log.info("features.write", rows=len(features), cols=features.shape[1], path=str(out_path))


if __name__ == "__main__":
    main()
