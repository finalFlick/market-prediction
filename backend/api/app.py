"""FastAPI application factory.

Defines the read-only HTTP surface consumed by the Next.js dashboard:

    /api/trades      — recent trades (filterable)
    /api/strategies  — registered strategies
    /api/signals     — signal hypotheses + status
    /api/backtests   — backtest runs and metrics
    /api/system      — health, version, runtime metrics

Mutations to risk, execution, or model artifacts are NOT exposed here.
The trading engine is the only writer to those tables.
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import asynccontextmanager
from importlib.metadata import PackageNotFoundError, version

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from backend.api.routers import backtests, learnings, runs, signals, sse, strategies, system, trades
from data.seeds.config_loader import seed_config_kv
from monitoring.logger import get_logger
from runs.orchestrator import RunOrchestrator

try:
    from prometheus_client import CONTENT_TYPE_LATEST as _PROM_CT
    from prometheus_client import generate_latest as _generate_latest
except ImportError:
    CONTENT_TYPE_LATEST: str | None = None
    generate_latest: Callable[[], bytes] | None = None
else:
    CONTENT_TYPE_LATEST = str(_PROM_CT)
    generate_latest = _generate_latest

log = get_logger(__name__)


def _version() -> str:
    try:
        return version("trading-lab")
    except PackageNotFoundError:
        return "0.0.0+local"


@asynccontextmanager
async def _lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    log.info("api.boot", version=_version())
    seeded = seed_config_kv()
    log.info("api.boot.config_seeded", n=seeded)
    n, _ = RunOrchestrator().on_boot()
    if n:
        log.warning("api.boot.recovery", transitioned=n)
    yield
    log.info("api.shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="trading-lab API",
        version=_version(),
        description=(
            "Read-only views over trades, strategies, signals, backtests, runs, and system status."
        ),
        lifespan=_lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
    app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
    app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
    app.include_router(backtests.router, prefix="/api/backtests", tags=["backtests"])
    app.include_router(runs.router, prefix="/api/runs", tags=["runs"])
    app.include_router(learnings.router, prefix="/api/learnings", tags=["learnings"])
    app.include_router(sse.router, prefix="/api/sse", tags=["sse"])
    app.include_router(system.router, prefix="/api/system", tags=["system"])

    if generate_latest is not None and CONTENT_TYPE_LATEST is not None:

        @app.get("/metrics")
        def _prometheus_metrics() -> Response:
            return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    return app


app = create_app()
