"""Run engine error types."""


class RunIsolationViolation(Exception):  # noqa: N818
    """A writer attempted to persist state for a run_id different from the active context."""


class RunConfigFrozenError(Exception):
    """Mutation was attempted on an immutable :class:`RunConfig`."""


class LiveTriggerForbidden(Exception):  # noqa: N818
    """An AI/LLM trigger tried to start a run in live mode."""


class RunOrchestratorError(Exception):
    """Base orchestration failure."""


__all__ = [
    "LiveTriggerForbidden",
    "RunConfigFrozenError",
    "RunIsolationViolation",
    "RunOrchestratorError",
]
