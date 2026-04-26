# FastAPI backend container.
# Reuses the base image conventions of the trading-engine but ships only the
# read-only HTTP surface and its dependencies.

FROM trading-base AS prod

RUN useradd --create-home --uid 1000 api
WORKDIR /app

COPY data ./data
COPY research ./research
COPY strategies ./strategies
COPY risk ./risk
COPY backtests ./backtests
COPY execution ./execution
COPY monitoring ./monitoring
COPY runs ./runs
COPY backend ./backend

RUN chown -R api:api /app
USER api

ENV ENV=prod API_HOST=0.0.0.0 API_PORT=8000 \
    DUCKDB_PATH=/app/data/market.duckdb LOG_LEVEL=INFO

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -fsS http://localhost:8000/api/system/health || exit 1

CMD ["uvicorn", "backend.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
