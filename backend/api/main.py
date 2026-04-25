"""Entrypoint: `python -m backend.api.main` or `uvicorn backend.api.app:app`."""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    uvicorn.run(
        "backend.api.app:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("ENV", "dev") == "dev",
    )


if __name__ == "__main__":
    main()
