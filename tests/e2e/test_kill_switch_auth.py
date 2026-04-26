"""Operator kill-switch auth: correct key succeeds, missing/wrong key → 401."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.api.app import create_app


@pytest.fixture()
def client_with_key(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("OPERATOR_API_KEY", "test-secret-key-123")
    return TestClient(create_app())


@pytest.mark.e2e
def test_engage_without_key_returns_401(client_with_key: TestClient) -> None:
    r = client_with_key.post("/api/system/kill-switch/engage")
    assert r.status_code == 401


@pytest.mark.e2e
def test_engage_with_wrong_key_returns_401(client_with_key: TestClient) -> None:
    r = client_with_key.post(
        "/api/system/kill-switch/engage",
        headers={"X-Operator-Key": "wrong-key"},
    )
    assert r.status_code == 401


@pytest.mark.e2e
def test_engage_with_correct_key_succeeds(client_with_key: TestClient) -> None:
    r = client_with_key.post(
        "/api/system/kill-switch/engage",
        headers={"X-Operator-Key": "test-secret-key-123"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "engaged"


@pytest.mark.e2e
def test_clear_with_correct_key_succeeds(client_with_key: TestClient) -> None:
    r = client_with_key.post(
        "/api/system/kill-switch/clear",
        headers={"X-Operator-Key": "test-secret-key-123"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "cleared"
