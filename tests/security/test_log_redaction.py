"""Verify the structlog processor scrubs known secret-bearing fields."""

from __future__ import annotations

import pytest

from monitoring.logger import _redact


@pytest.mark.security
@pytest.mark.parametrize(
    "key",
    [
        "api_key",
        "API_KEY",
        "api_secret",
        "secret",
        "password",
        "passphrase",
        "signature",
        "authorization",
        "token",
        "access_token",
        "refresh_token",
    ],
)
def test_redact_scrubs_known_keys(key: str) -> None:
    out = _redact(object(), "info", {key: "supersecret", "ok": "value"})
    assert out[key] == "***REDACTED***"
    assert out["ok"] == "value"


@pytest.mark.security
def test_redact_leaves_unrelated_keys_alone() -> None:
    out = _redact(object(), "info", {"trade_id": "T-1", "qty": 0.25})
    assert out == {"trade_id": "T-1", "qty": 0.25}
