from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from monitoring.canonical_json import NonFiniteFloatError, canonical_dumps


def test_sorted_keys() -> None:
    assert canonical_dumps({"b": 1, "a": 2}) == '{"a":2,"b":1}'


def test_decimal_string_in_output() -> None:
    s = canonical_dumps({"x": Decimal("1.1")})
    assert '"1.1"' in s


def test_datetime_utc_z() -> None:
    d = datetime(2024, 1, 2, 3, 4, 5, tzinfo=UTC)
    s = canonical_dumps({"t": d})
    assert "2024-01-02T03:04:05Z" in s


def test_rejects_non_finite_float() -> None:
    with pytest.raises(NonFiniteFloatError):
        canonical_dumps({"x": float("nan")})


def test_bytes_hex() -> None:
    s = canonical_dumps({"b": b"ab"})
    assert "6162" in s
