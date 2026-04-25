"""Abstract ingester contract for any exchange."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Iterable
from datetime import datetime

from data.types import OHLCVBar, Timeframe


class Ingester(ABC):
    """Pulls historical bars and (optionally) streams live bars from an exchange."""

    name: str

    @abstractmethod
    def fetch_historical(
        self,
        symbol: str,
        timeframe: Timeframe,
        start: datetime,
        end: datetime,
    ) -> Iterable[OHLCVBar]:
        """Yield closed bars in `[start, end]`, oldest first."""

    @abstractmethod
    def stream_live(
        self,
        symbol: str,
        timeframe: Timeframe,
    ) -> AsyncIterator[OHLCVBar]:
        """Yield closed bars in real time as the exchange emits them."""
