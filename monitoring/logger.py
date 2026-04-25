"""Structured logging used by every module.

JSON to stdout in non-dev environments, console-rendered in dev. Always
include the module name and a UTC timestamp.
"""

from __future__ import annotations

import logging
import os
import sys
from collections.abc import MutableMapping
from typing import Any, cast

import structlog

_CONFIGURED = False

# Per `.cursor/rules/security.mdc`: never log raw credentials.
_REDACT_KEYS = frozenset(
    {
        "api_key",
        "api_secret",
        "secret",
        "password",
        "passphrase",
        "signature",
        "authorization",
        "token",
        "access_token",
        "refresh_token",
    }
)
_REDACTED = "***REDACTED***"


def _redact(
    _logger: object, _name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """structlog processor: redact known secret-bearing keys (case-insensitive)."""
    for k in list(event_dict):
        if k.lower() in _REDACT_KEYS:
            event_dict[k] = _REDACTED
    return event_dict


def _configure(level: str = "INFO", as_json: bool | None = None) -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    if as_json is None:
        as_json = os.getenv("ENV", "dev").lower() != "dev"

    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        timestamper,
        _redact,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer()
        if as_json
        else structlog.dev.ConsoleRenderer(colors=True)
    )

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
    _CONFIGURED = True


def get_logger(name: str, **initial_values: Any) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger bound with `module=name` and any extras."""
    _configure(level=os.getenv("LOG_LEVEL", "INFO"))
    bound = structlog.get_logger(name).bind(module=name, **initial_values)
    return cast(structlog.stdlib.BoundLogger, bound)
