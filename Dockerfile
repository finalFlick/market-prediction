# Trading engine container.
# Runs the strategy + risk + execution loop. Same image is used for ad-hoc
# CLI invocations (data ingest, feature build, model train, backtest run).

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps for lightgbm / xgboost / pyarrow / duckdb.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgomp1 \
        curl \
        && rm -rf /var/lib/apt/lists/*

# Non-root runtime user.
RUN useradd --create-home --uid 1000 trader
WORKDIR /app

COPY pyproject.toml README.md ./
RUN pip install --upgrade pip && pip install -e .

COPY data ./data
COPY research ./research
COPY strategies ./strategies
COPY risk ./risk
COPY backtests ./backtests
COPY execution ./execution
COPY monitoring ./monitoring
COPY configs ./configs
COPY backend ./backend

RUN mkdir -p /app/data/raw /app/data/processed /app/backtests/results \
    && chown -R trader:trader /app

USER trader

ENV ENV=prod \
    DUCKDB_PATH=/app/data/market.duckdb \
    LOG_LEVEL=INFO

# Default: run the live execution loop with the paper broker.
CMD ["python", "-m", "execution.runner", "--broker", "paper", "--strategy", "strategies.examples.momentum_xover"]
