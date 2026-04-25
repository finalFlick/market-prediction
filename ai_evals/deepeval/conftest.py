"""Shared fixtures: load offline responses and decide online vs offline mode."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture(scope="session")
def offline_responses() -> dict[str, object]:
    return json.loads((_FIXTURES / "offline_responses.json").read_text())


@pytest.fixture(scope="session")
def online() -> bool:
    return os.getenv("OFFLINE_LLM", "true").lower() not in {"1", "true", "yes"}
