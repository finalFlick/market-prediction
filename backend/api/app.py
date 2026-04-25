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

from contextlib import asynccontextmanager
from importlib.metadata import PackageNotFoundError, version

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routers import backtests, signals, strategies, system, trades
from monitoring.logger import get_logger

log = get_logger(__name__)


def _version() -> str:
    try:
        return version("trading-lab")
    except PackageNotFoundError:
        return "0.0.0+local"


@asynccontextmanager
async def _lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    log.info("api.boot", version=_version())
    yield
    log.info("api.shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title="trading-lab API",
        version=_version(),
        description=(
            "Read-only views over trades, strategies, signals, "
            "backtests, and system status."
        ),
        lifespan=_lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
    app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
    app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
    app.include_router(backtests.router, prefix="/api/backtests", tags=["backtests"])
    app.include_router(system.router, prefix="/api/system", tags=["system"])
    return app


app = create_app()
