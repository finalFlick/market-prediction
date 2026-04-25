"""Contract tests for the model-reasoning prompt."""

from __future__ import annotations

import re

from research.llm.prompts import render


def _resolve(online: bool, response_text: str) -> str:
    if online:
        from research.llm.client import OllamaClient

        client = OllamaClient()
        system, prompt = render(
            "model_reasoning",
            model="lgbm_v3",
            prediction="+0.42σ over 1h",
            top_features="rv_24h_z=1.8; ret_1h=0.6; rsi_14=0.55",
        )
        return client.chat(prompt, system=system, max_tokens=256).text
    return response_text


def test_model_reasoning_word_budget(offline_responses: dict[str, object], online: bool) -> None:
    text = _resolve(online, str(offline_responses["model_reasoning"]))
    words = re.findall(r"\w+", text)
    assert 0 < len(words) <= 200, f"expected <=200 words, got {len(words)}"


def test_model_reasoning_references_features(
    offline_responses: dict[str, object], online: bool
) -> None:
    text = _resolve(online, str(offline_responses["model_reasoning"])).lower()
    assert any(
        term in text for term in ("vol", "rsi", "momentum", "feature")
    ), "must reference at least one feature"


def test_model_reasoning_no_certainty_claims(
    offline_responses: dict[str, object], online: bool
) -> None:
    text = _resolve(online, str(offline_responses["model_reasoning"])).lower()
    for phrase in ("definitely", "guaranteed", "always profitable"):
        assert phrase not in text
