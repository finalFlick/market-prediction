"""CLI: pull historical bars and write them to the OHLCV store."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import click

from data.ingest.base import Ingester
from data.ingest.binance import BinanceIngester
from data.ingest.binance_public import BinancePublicIngester
from data.ingest.coinbase import CoinbaseIngester
from data.ingest.coinbase_public import CoinbasePublicIngester
from data.ingest.yfinance_source import YFinanceIngester
from data.store import OHLCVStore
from data.types import Exchange, Timeframe
from monitoring.logger import get_logger

log = get_logger(__name__)

_SOURCE_EXCHANGE: dict[str, Exchange] = {
    "binance": Exchange.BINANCE,
    "binance-auth": Exchange.BINANCE,
    "coinbase": Exchange.COINBASE,
    "coinbase-auth": Exchange.COINBASE,
    "yahoo": Exchange.YAHOO,
}


def _make_ingester(source: str) -> Ingester:
    if source == "binance":
        return BinancePublicIngester()
    if source == "coinbase":
        return CoinbasePublicIngester()
    if source == "yahoo":
        return YFinanceIngester()
    if source == "binance-auth":
        return BinanceIngester()
    if source == "coinbase-auth":
        return CoinbaseIngester()
    msg = f"unknown source: {source!r}"
    raise ValueError(msg)


@click.command()
@click.option(
    "--source",
    type=click.Choice(
        ["binance", "coinbase", "yahoo", "binance-auth", "coinbase-auth"],
        case_sensitive=False,
    ),
    default="binance",
    show_default=True,
    help="Public REST (default) or keyed stub ingesters (auth) for later CCXT work.",
)
@click.option(
    "--exchange",
    type=click.Choice([e.value for e in Exchange]),
    default=None,
    help="If set, must match the logical exchange for --source (else inferred).",
)
@click.option("--symbol", required=True)
@click.option(
    "--timeframe", type=click.Choice([t.value for t in Timeframe]), default=Timeframe.H1.value
)
@click.option("--days", type=int, default=365, show_default=True)
@click.option("--db-path", type=click.Path(), default=None, help="Override DUCKDB_PATH.")
def main(
    source: str,
    exchange: str | None,
    symbol: str,
    timeframe: str,
    days: int,
    db_path: str | None,
) -> None:
    """Fetch the last N days of bars for SYMBOL and write to the store."""
    src = source.lower()
    expected = _SOURCE_EXCHANGE[src]
    ex = expected if exchange is None else Exchange(exchange)
    if ex is not expected:
        raise click.BadParameter(
            f"--exchange {ex.value!r} does not match --source {src!r} "
            f"(expected {expected.value!r} or omit --exchange).",
        )
    tf = Timeframe(timeframe)
    end = datetime.now(tz=UTC)
    start = end - timedelta(days=days)
    min_days_intraday = 7
    if (
        src == "yahoo"
        and (end - start).total_seconds() < min_days_intraday * 24 * 3600
        and tf
        in (
            Timeframe.M1,
            Timeframe.M5,
            Timeframe.M15,
        )
    ):
        log.warning(
            "ingest.yahoo_intraday_range",
            note="yfinance may return empty for very short windows on sub-daily; "
            "try --days 8+ or 1d timeframe.",
        )

    ingester = _make_ingester(src)
    log.info(
        "ingest.start",
        source=src,
        exchange=ex.value,
        symbol=symbol,
        timeframe=tf.value,
        days=days,
    )

    with OHLCVStore(db_path) as store:
        bars = list(ingester.fetch_historical(symbol, tf, start, end))
        n = store.upsert(bars)
        log.info("ingest.done", source=src, exchange=ex.value, symbol=symbol, rows=n)


if __name__ == "__main__":
    main()
