"""Coinbase public ingester with mocked HTTP."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from data.ingest.coinbase_public import CoinbasePublicIngester, _product_id
from data.types import Timeframe


def test_product_id_normalization() -> None:
    assert _product_id("BTC-USD") == "BTC-USD"
    assert _product_id("btc-usd") == "BTC-USD"
    assert _product_id("BTCUSDT") == "BTC-USDT"


def test_coinbase_public_fetch_historical() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = datetime(2024, 1, 1, 12, tzinfo=UTC)
    row = [1_704_067_200, 100.0, 110.0, 105.0, 1.0]
    ing = CoinbasePublicIngester()
    with patch.object(CoinbasePublicIngester, "_get_candles", return_value=[row]):
        bars = list(ing.fetch_historical("BTC-USD", Timeframe.H1, start, end))
    assert len(bars) == 1
    assert bars[0].exchange.value == "coinbase"
    assert bars[0].close == 105.0


def test_coinbase_get_candles_uses_httpx() -> None:
    ing = CoinbasePublicIngester()
    mock_resp = MagicMock()
    mock_resp.json.return_value = []
    mock_resp.raise_for_status = MagicMock()
    with patch("data.ingest.coinbase_public.httpx.Client") as client_cls:
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = None
        client.get.return_value = mock_resp
        client_cls.return_value = client
        out = ing._get_candles("BTC-USD", 3600, "2024-01-01T00:00:00", "2024-01-01T01:00:00")
    assert out == []
