"""GET /api/system — health, version, and runtime metrics."""

from __future__ import annotations

import os
import time
from importlib.metadata import PackageNotFoundError, version

from fastapi import APIRouter
from pydantic import BaseModel

from data.db import connect
from monitoring.metrics import snapshot

router = APIRouter()
_BOOT_TS = time.time()


class HealthOut(BaseModel):
    status: str
    version: str
    env: str
    uptime_s: float
    db_ok: bool
    redis_ok: bool


class MetricsOut(BaseModel):
    metrics: dict[str, float]


def _version() -> str:
    try:
        return version("trading-lab")
    except PackageNotFoundError:
        return "0.0.0+local"


def _check_db() -> bool:
    try:
        conn = connect()
        conn.execute("SELECT 1").fetchone()
        conn.close()
        return True
    except Exception:
        return False


def _check_redis() -> bool:
    url = os.getenv("REDIS_URL")
    if not url:
        return False
    try:
        import redis  # noqa: PLC0415

        client = redis.Redis.from_url(url, socket_timeout=1.0)
        return bool(client.ping())
    except Exception:
        return False


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut(
        status="ok",
        version=_version(),
        env=os.getenv("ENV", "dev"),
        uptime_s=time.time() - _BOOT_TS,
        db_ok=_check_db(),
        redis_ok=_check_redis(),
    )


@router.get("/metrics", response_model=MetricsOut)
def metrics() -> MetricsOut:
    return MetricsOut(metrics=dict(snapshot()))
