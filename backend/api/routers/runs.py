"""`GET /api/runs` — read-only run list + detail (MVP-0)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from runs.orchestrator import RunOrchestrator

router = APIRouter()


@router.get("")
def list_runs(
    limit: int = Query(200, ge=1, le=1000),
    status: str | None = Query(None, description="Filter by status, e.g. succeeded"),
    run_type: str | None = Query(None, description="Filter by run_type, e.g. backtest"),
) -> dict[str, Any]:
    o = RunOrchestrator()
    items = o.list_runs(limit=limit)
    if status:
        items = [i for i in items if i.get("status") == status]
    if run_type:
        items = [i for i in items if i.get("run_type") == run_type]
    return {"items": items}


@router.get("/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    o = RunOrchestrator()
    r = o.get_run(run_id)
    if r is None:
        raise HTTPException(status_code=404, detail="run not found")
    return r
