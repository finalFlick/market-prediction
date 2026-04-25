"""Local LLM helpers for research only.

Per `.cursor/rules/llm-usage.mdc`, modules in `execution/` MUST NOT import
anything from `research.llm`. CI enforces this with an import-graph test
in `tests/security/test_llm_isolation.py`.
"""

from research.llm.client import LLMResponse, OllamaClient, chat
from research.llm.prompts import PROMPTS, render

__all__ = ["chat", "LLMResponse", "OllamaClient", "PROMPTS", "render"]
