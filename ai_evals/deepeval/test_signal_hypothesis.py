"""Contract tests for the signal hypothesis prompt.

In offline mode the recorded fixture is used. In online mode (OFFLINE_LLM=false)
we hit the local Ollama via `research.llm.client.OllamaClient`.
"""

from __future__ import annotations

import json

import pytest

from research.llm.prompts import render

REQUIRED_KEYS = {"name", "intuition", "timeframe", "expected_horizon", "falsification"}
FORBIDDEN = {"deploy", "go live", "ship to production"}


def _resolve(online: bool, response_text: str) -> str:
    if online:
        from research.llm.client import OllamaClient

        client = OllamaClient()
        system, prompt = render(
            "signal_hypothesis",
            universe="BTCUSDT, ETHUSDT, SOLUSDT",
            regime="post-halving consolidation, declining vol, high funding",
            existing="SIG-001, SIG-002, SIG-003",
        )
        return client.chat(prompt, system=system, max_tokens=256).text
    return response_text


def test_signal_hypothesis_is_valid_json(
    offline_responses: dict[str, object], online: bool
) -> None:
    fixture = offline_responses["signal_hypothesis"]
    text = _resolve(online, json.dumps(fixture))
    obj = json.loads(text)
    missing = REQUIRED_KEYS - set(obj)
    assert not missing, f"missing keys: {missing}"


def test_signal_hypothesis_no_deploy_language(
    offline_responses: dict[str, object], online: bool
) -> None:
    fixture = offline_responses["signal_hypothesis"]
    text = _resolve(online, json.dumps(fixture)).lower()
    for term in FORBIDDEN:
        assert term not in text, f"forbidden phrase '{term}' present"


@pytest.mark.parametrize(
    "field",
    ["name", "intuition", "timeframe", "expected_horizon", "falsification"],
)
def test_signal_hypothesis_fields_non_empty(
    offline_responses: dict[str, object], online: bool, field: str
) -> None:
    fixture = offline_responses["signal_hypothesis"]
    text = _resolve(online, json.dumps(fixture))
    obj = json.loads(text)
    assert isinstance(obj[field], str) and obj[field].strip()
