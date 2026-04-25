"""Risk-specific errors."""


class RiskCheckRejected(Exception):
    """Raised when an order or portfolio change violates a risk limit."""

    def __init__(self, rule: str, message: str) -> None:
        super().__init__(f"[{rule}] {message}")
        self.rule = rule
        self.message = message
