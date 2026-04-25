"""CLI: pull historical bars and write them to the OHLCV store."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import click

from data.ingest.base import Ingester
from data.ingest.binance import BinanceIngester
from data.ingest.coinbase import CoinbaseIngester
from data.store import OHLCVStore
from data.types import Exchange, Timeframe
from monitoring.logger import get_logger

log = get_logger(__name__)

_INGESTERS: dict[Exchange, type[Ingester]] = {
    Exchange.BINANCE: BinanceIngester,
    Exchange.COINBASE: CoinbaseIngester,
}


@click.command()
@click.option("--exchange", type=click.Choice([e.value for e in Exchange]), required=True)
@click.option("--symbol", required=True)
@click.option(
    "--timeframe", type=click.Choice([t.value for t in Timeframe]), default=Timeframe.H1.value
)
@click.option("--days", type=int, default=365, show_default=True)
@click.option("--db-path", type=click.Path(), default=None, help="Override DUCKDB_PATH.")
def main(exchange: str, symbol: str, timeframe: str, days: int, db_path: str | None) -> None:
    """Fetch the last N days of bars for SYMBOL and write to the store."""
    ex = Exchange(exchange)
    tf = Timeframe(timeframe)
    end = datetime.now(tz=UTC)
    start = end - timedelta(days=days)

    ingester_cls = _INGESTERS[ex]
    ingester = ingester_cls()  # default constructor (testnet/sandbox=True)

    log.info("ingest.start", exchange=ex.value, symbol=symbol, timeframe=tf.value, days=days)

    with OHLCVStore(db_path) as store:
        bars = list(ingester.fetch_historical(symbol, tf, start, end))
        n = store.upsert(bars)
        log.info("ingest.done", exchange=ex.value, symbol=symbol, rows=n)


if __name__ == "__main__":
    main()
