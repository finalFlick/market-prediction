"""Binance public ingester with mocked HTTP."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from data.ingest.binance_public import BinancePublicIngester
from data.types import Timeframe


def test_binance_public_fetch_historical_one_page() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = datetime(2024, 1, 2, tzinfo=UTC)
    # One kline: [openTime, o, h, l, c, vol, closeTime, quoteVol, ...]
    row = [
        1_704_067_200_000,
        "1",
        "2",
        "0.5",
        "1.5",
        "10",
        1_704_070_800_000,
        "15",
    ]
    ing = BinancePublicIngester()
    with patch.object(BinancePublicIngester, "_get_klines", return_value=[row]) as m:
        bars = list(ing.fetch_historical("BTCUSDT", Timeframe.H1, start, end))
    m.assert_called()
    assert len(bars) == 1
    b = bars[0]
    assert b.exchange.value == "binance"
    assert b.symbol == "BTCUSDT"
    assert b.open == 1.0
    assert b.quote_volume == 15.0


def test_binance_public_get_klines_uses_httpx() -> None:
    ing = BinancePublicIngester()
    mock_resp = MagicMock()
    mock_resp.json.return_value = []
    mock_resp.raise_for_status = MagicMock()
    with patch("data.ingest.binance_public.httpx.Client") as client_cls:
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = None
        client.get.return_value = mock_resp
        client_cls.return_value = client
        out = ing._get_klines(
            symbol="ETHUSDT",
            interval="1h",
            start_ms=1,
            end_ms=2,
            limit=10,
        )
    assert out == []
    client.get.assert_called_once()
