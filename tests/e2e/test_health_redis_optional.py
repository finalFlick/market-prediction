"""Health reflects optional Redis (no false failure when URL unset)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.api.app import create_app


@pytest.mark.e2e
def test_health_redis_disabled_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("REDIS_URL", raising=False)
    client = TestClient(create_app())
    r = client.get("/api/system/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("redis_disabled") is True
    assert body.get("redis_ok") is True
