"""Versioned prompt library.

Prompts are not free-form strings scattered through the codebase. Every
prompt has a name, a template, and a version. The `ai_evals/` harness
references them by name so eval scores are tied to a specific revision.
"""

from __future__ import annotations

from dataclasses import dataclass
from string import Template
from typing import Final


@dataclass(frozen=True)
class Prompt:
    name: str
    version: str
    system: str
    template: str

    def render(self, **values: object) -> tuple[str, str]:
        return self.system, Template(self.template).safe_substitute(values)


SIGNAL_HYPOTHESIS_V1: Final = Prompt(
    name="signal_hypothesis",
    version="v1",
    system=(
        "You are a quantitative researcher. Propose ONE testable trading "
        "signal hypothesis. Be concise (<=120 words). Output JSON with keys: "
        "name, intuition, timeframe, expected_horizon, falsification."
    ),
    template=(
        "Universe: ${universe}\n"
        "Recent regime: ${regime}\n"
        "Existing signals to avoid duplicating: ${existing}\n"
    ),
)


STRATEGY_ANALYSIS_V1: Final = Prompt(
    name="strategy_analysis",
    version="v1",
    system=(
        "You are reviewing a backtest report. Identify weaknesses, possible "
        "look-ahead, and suggested ablations. Do NOT recommend deploying. "
        "Output JSON with keys: weaknesses, leakage_risks, ablations."
    ),
    template=(
        "Strategy: ${strategy}\n"
        "Metrics:\n${metrics}\n"
        "Trade summary:\n${trades_summary}\n"
    ),
)


MODEL_REASONING_V1: Final = Prompt(
    name="model_reasoning",
    version="v1",
    system=(
        "Explain why the model produced this prediction in plain language. "
        "Reference top features by name. Be skeptical: highlight any feature "
        "that may be noisy or regime-specific. Output plain text, <=150 words."
    ),
    template=(
        "Model: ${model}\nPrediction: ${prediction}\n"
        "Top features:\n${top_features}\n"
    ),
)


PROMPTS: Final[dict[str, Prompt]] = {
    SIGNAL_HYPOTHESIS_V1.name: SIGNAL_HYPOTHESIS_V1,
    STRATEGY_ANALYSIS_V1.name: STRATEGY_ANALYSIS_V1,
    MODEL_REASONING_V1.name: MODEL_REASONING_V1,
}


def render(name: str, **values: object) -> tuple[str, str]:
    """Render `(system, prompt)` for the named prompt."""
    if name not in PROMPTS:
        raise KeyError(f"unknown prompt '{name}'; known: {list(PROMPTS)}")
    return PROMPTS[name].render(**values)
