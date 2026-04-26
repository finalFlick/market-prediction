"""`GET /api/sse/runs/{run_id}` — Server-Sent Events for run lifecycle (MVP-0).

Streams durable events from ``run_events_durable`` for the given run.
Consumers receive ``text/event-stream`` newline-delimited JSON objects.

Design note: this is the minimal SSE surface described in design.md §Backend
MVP-0 deliverables.  The full Redis Streams fan-out (live ``XREAD`` with
blocking reads) is deferred to v1 per ``docs/MVP0_READINESS.md``.
"""

from __future__ import annotations

import json
from collections.abc import Iterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from data.db import connect

router = APIRouter()


def _sse_line(data: dict) -> str:  # type: ignore[type-arg]
    return f"data: {json.dumps(data, default=str)}\n\n"


def _stream_run_events(run_id: str) -> Iterator[str]:
    conn = connect()
    try:
        rows = conn.execute(
            """
            SELECT stream, event_id, natural_key, payload_json, created_at
            FROM run_events_durable
            WHERE natural_key LIKE ?
            ORDER BY created_at
            """,
            [f"{run_id}%"],
        ).fetchall()
        if not rows:
            yield _sse_line({"run_id": run_id, "kind": "no_events", "count": 0})
        else:
            for stream, event_id, natural_key, payload_json, created_at in rows:
                payload = json.loads(payload_json) if isinstance(payload_json, str) else {}
                yield _sse_line(
                    {
                        "run_id": run_id,
                        "stream": stream,
                        "event_id": event_id,
                        "natural_key": natural_key,
                        "payload": payload,
                        "created_at": str(created_at),
                    }
                )
        yield 'data: {"kind": "done"}\n\n'
    finally:
        conn.close()


@router.get("/runs/{run_id}")
def run_events_sse(run_id: str) -> StreamingResponse:
    """Stream durable run events as Server-Sent Events."""
    return StreamingResponse(
        _stream_run_events(run_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
