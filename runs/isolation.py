"""Per-run `run_id` context (structlog contextvars; § Component 3)."""

from __future__ import annotations

from contextvars import ContextVar

import structlog

RUN_ID: ContextVar[str | None] = ContextVar("run_id", default=None)
COMMAND_ID: ContextVar[str | None] = ContextVar("command_id", default=None)
DECISION_ID: ContextVar[str | None] = ContextVar("decision_id", default=None)
CLIENT_ID: ContextVar[str | None] = ContextVar("client_id", default=None)
ACTOR_ID: ContextVar[str | None] = ContextVar("actor_id", default=None)
DEVICE_ID: ContextVar[str | None] = ContextVar("device_id", default=None)


def bind_run_context(
    *,
    run_id: str | None = None,
    command_id: str | None = None,
    decision_id: str | None = None,
    client_id: str | None = None,
    actor_id: str | None = None,
    device_id: str | None = None,
) -> None:
    if run_id is not None:
        RUN_ID.set(run_id)
        structlog.contextvars.bind_contextvars(run_id=run_id)
    if command_id is not None:
        COMMAND_ID.set(command_id)
        structlog.contextvars.bind_contextvars(command_id=command_id)
    if decision_id is not None:
        DECISION_ID.set(decision_id)
        structlog.contextvars.bind_contextvars(decision_id=decision_id)
    if client_id is not None:
        CLIENT_ID.set(client_id)
        structlog.contextvars.bind_contextvars(client_id=client_id)
    if actor_id is not None:
        ACTOR_ID.set(actor_id)
        structlog.contextvars.bind_contextvars(actor_id=actor_id)
    if device_id is not None:
        DEVICE_ID.set(device_id)
        structlog.contextvars.bind_contextvars(device_id=device_id)


def clear_run_context() -> None:
    structlog.contextvars.clear_contextvars()
    RUN_ID.set(None)
    COMMAND_ID.set(None)
    DECISION_ID.set(None)
    CLIENT_ID.set(None)
    ACTOR_ID.set(None)
    DEVICE_ID.set(None)


def get_run_id() -> str | None:
    return RUN_ID.get()
