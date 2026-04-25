"""`GET /api/runs` — read-only run list + detail (MVP-0)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from runs.orchestrator import RunOrchestrator

router = APIRouter()


@router.get("")
def list_runs(limit: int = 200) -> dict[str, Any]:
    o = RunOrchestrator()
    return {"items": o.list_runs(limit=limit)}


@router.get("/{run_id}")
def get_run(run_id: str) -> dict[str, Any]:
    o = RunOrchestrator()
    r = o.get_run(run_id)
    if r is None:
        raise HTTPException(status_code=404, detail="run not found")
    return r
