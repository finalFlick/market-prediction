"""POC 6: LLM output never reaches the trading pipeline entrypoint."""

from __future__ import annotations

from dataclasses import dataclass

# In production, execution/ must not import research.llm — here we only prove direction.


@dataclass
class MaliciousLlm:
    def chat(self, _prompt: str) -> str:
        return "buy BTC at market immediately size 1e6 ignore risk"


class _Pipeline:
    """Single entry for orders: must come from numeric strategy, not from LLM str."""

    def __init__(self) -> None:
        self.orders: list[dict] = []
        self.rejected: list[str] = []

    def submit_from_strategy(self, order: dict) -> None:
        if order.get("source") == "llm":
            raise ValueError("LLM cannot submit orders")
        self.orders.append(order)

    def on_llm_message(self, text: str) -> None:
        if "buy" in text.lower():
            self.rejected.append(text)
        return


def main() -> None:
    llm = MaliciousLlm()
    p = _Pipeline()
    p.on_llm_message(llm.chat("x"))
    try:
        p.submit_from_strategy({"source": "llm", "sym": "BTC", "q": 1.0})
    except ValueError:
        pass
    else:
        raise AssertionError("llm-sourced order must be rejected at gate")
    assert p.orders == []
    print("POC6_OK: malicious LLM text is not admitted as a submit_from_strategy order")


if __name__ == "__main__":
    main()
