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
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse, Response
from starlette.staticfiles import StaticFiles

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

_STATIC_DIR = Path(__file__).resolve().parent / "static"
_SWAGGER_CSS_URL = "/static/swagger-trading-lab.css"


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
        docs_url=None,
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

    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="api_static")

    @app.get("/docs", include_in_schema=False)
    def _swagger_ui_html() -> HTMLResponse:
        # Render the stock Swagger UI (so the default CDN base stylesheet
        # still loads), then inject our override stylesheet inside <head>.
        # Passing swagger_css_url= would *replace* the base CSS instead of
        # supplementing it, which removes Swagger's layout entirely.
        base = get_swagger_ui_html(
            openapi_url=app.openapi_url or "/openapi.json",
            title=f"{app.title} — docs",
            swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
        )
        body = (
            bytes(base.body)
            .decode("utf-8")
            .replace(
                "</head>",
                f'<link rel="stylesheet" type="text/css" href="{_SWAGGER_CSS_URL}"></head>',
                1,
            )
        )
        return HTMLResponse(body)

    return app


app = create_app()
