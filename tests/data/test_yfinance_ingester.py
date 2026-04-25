"""YFinance ingester with mocked yfinance."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pandas as pd

from data.ingest.yfinance_source import YFinanceIngester
from data.types import Timeframe


def test_yfinance_fetch_historical() -> None:
    start = datetime(2024, 1, 1, tzinfo=UTC)
    end = datetime(2024, 3, 1, tzinfo=UTC)
    idx = pd.date_range("2024-01-02", periods=2, freq="D", tz="UTC")
    df = pd.DataFrame(
        {
            "Open": [10.0, 11.0],
            "High": [11.0, 12.0],
            "Low": [9.0, 10.0],
            "Close": [10.5, 11.5],
            "Volume": [100, 200],
        },
        index=idx,
    )
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = df

    ing = YFinanceIngester()
    with patch("data.ingest.yfinance_source._require_yfinance") as mock_yf:
        mock_mod = MagicMock()
        mock_mod.Ticker.return_value = mock_ticker
        mock_yf.return_value = mock_mod
        bars = list(ing.fetch_historical("AAPL", Timeframe.D1, start, end))

    assert len(bars) == 2
    assert bars[0].exchange.value == "yahoo"
    assert bars[0].symbol == "AAPL"
    assert bars[0].close == 10.5
