"""Contract tests for the strategy-analysis prompt."""

from __future__ import annotations

import json

from research.llm.prompts import render

REQUIRED_KEYS = {"weaknesses", "leakage_risks", "ablations"}
FORBIDDEN = {"deploy live", "go live", "ship to production"}


def _resolve(online: bool, response_text: str) -> str:
    if online:
        from research.llm.client import OllamaClient

        client = OllamaClient()
        system, prompt = render(
            "strategy_analysis",
            strategy="momentum_xover",
            metrics="sharpe=1.42 sortino=1.91 maxDD=-0.18 cagr=0.32",
            trades_summary="n=312 avg_hold=14 wl=168/144",
        )
        return client.chat(prompt, system=system, max_tokens=256).text
    return response_text


def test_strategy_analysis_shape(offline_responses: dict[str, object], online: bool) -> None:
    fixture = offline_responses["strategy_analysis"]
    obj = json.loads(_resolve(online, json.dumps(fixture)))
    missing = REQUIRED_KEYS - set(obj)
    assert not missing, f"missing keys: {missing}"
    for key in REQUIRED_KEYS:
        assert isinstance(obj[key], list) and obj[key], f"{key} empty"


def test_strategy_analysis_no_promotion_language(
    offline_responses: dict[str, object], online: bool
) -> None:
    text = _resolve(online, json.dumps(offline_responses["strategy_analysis"])).lower()
    for term in FORBIDDEN:
        assert term not in text


def test_strategy_analysis_calls_out_leakage(
    offline_responses: dict[str, object], online: bool
) -> None:
    obj = json.loads(_resolve(online, json.dumps(offline_responses["strategy_analysis"])))
    assert obj["leakage_risks"], "leakage_risks must be non-empty for any reviewed strategy"
