"""Bootstrap the FastAPI app in-process and exercise the read-only routes.

Uses the ASGI test client so no live server is required. Verifies the
shape of the responses matches the public Pydantic schema.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.api.app import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(create_app())


@pytest.mark.e2e
def test_health(client: TestClient) -> None:
    r = client.get("/api/system/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert "env" in body
    assert "audit_chain_ok" in body


@pytest.mark.e2e
@pytest.mark.parametrize(
    "path",
    [
        "/api/trades",
        "/api/strategies",
        "/api/signals",
        "/api/backtests",
        "/api/system/metrics",
        "/api/runs",
    ],
)
def test_get_endpoints_return_2xx(client: TestClient, path: str) -> None:
    r = client.get(path)
    assert r.status_code == 200, f"{path} -> {r.status_code} {r.text}"
