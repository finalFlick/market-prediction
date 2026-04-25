"""Thin wrapper around the local Ollama HTTP API.

Every call records prompt hash, model, temperature, and token counts via
`monitoring.logger`. Outputs that influence a research artifact are written
alongside the artifact under `data/processed/llm_features/<run_id>/`.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from monitoring.logger import get_logger
from monitoring.metrics import counter

log = get_logger(__name__)


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class OllamaClient:
    """Calls a local Ollama server. No third-party APIs are reachable from here."""

    def __init__(
        self,
        *,
        host: str | None = None,
        model: str | None = None,
        timeout_s: float = 60.0,
    ) -> None:
        self.host = host or os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct")
        self.timeout_s = timeout_s

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    def chat(
        self,
        prompt: str,
        *,
        system: str | None = None,
        temperature: float = 0.0,
        seed: int = 42,
        top_p: float = 0.9,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "seed": seed,
                "top_p": top_p,
                "num_predict": max_tokens,
            },
        }
        if system:
            payload["system"] = system

        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:12]
        log.info(
            "llm.request",
            model=self.model,
            prompt_hash=prompt_hash,
            temperature=temperature,
            seed=seed,
        )

        with httpx.Client(timeout=self.timeout_s) as client:
            r = client.post(f"{self.host}/api/generate", json=payload)
            r.raise_for_status()
            data = r.json()

        response = LLMResponse(
            text=data.get("response", ""),
            model=str(self.model),
            prompt_tokens=int(data.get("prompt_eval_count", 0)),
            completion_tokens=int(data.get("eval_count", 0)),
            total_tokens=int(data.get("prompt_eval_count", 0)) + int(data.get("eval_count", 0)),
        )
        counter("llm.tokens", value=response.total_tokens, model=self.model)
        log.info(
            "llm.response",
            model=self.model,
            prompt_hash=prompt_hash,
            total_tokens=response.total_tokens,
        )
        return response


_default_client: OllamaClient | None = None


def chat(prompt: str, **kwargs: Any) -> LLMResponse:
    """Module-level convenience that uses a singleton OllamaClient."""
    global _default_client
    if _default_client is None:
        _default_client = OllamaClient()
    return _default_client.chat(prompt, **kwargs)


def manifest_payload(prompt: str, response: LLMResponse) -> dict[str, Any]:
    """Build a JSON-serializable record for an LLM call (audit trail)."""
    return {
        "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest()[:12],
        "prompt": prompt,
        "response_text": response.text,
        "model": response.model,
        "prompt_tokens": response.prompt_tokens,
        "completion_tokens": response.completion_tokens,
        "total_tokens": response.total_tokens,
    }


def _smoke() -> None:  # pragma: no cover - manual probe
    print(json.dumps(manifest_payload("hello", chat("hello", max_tokens=8)), indent=2))
