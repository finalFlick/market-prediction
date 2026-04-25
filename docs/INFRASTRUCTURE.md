# INFRASTRUCTURE

Where the system runs and how the pieces are wired.

## Host

- **Unraid server**, dockerd available, `trading-net` docker network shared
  across community-app containers.
- **GPU passthrough** to `ollama` for local LLM inference. The trading
  engine itself is CPU-only; PyTorch can use the GPU when training models
  from a research notebook on the host (out of band of `docker compose`).

## Containers

| Container          | Source                | Owner of …                                     |
|--------------------|-----------------------|------------------------------------------------|
| `trading-frontend` | `frontend/Dockerfile` | Next.js dashboard, port 3000                   |
| `trading-backend`  | `backend/Dockerfile`  | FastAPI read-only API, port 8000               |
| `trading-engine`   | `Dockerfile` (root)   | Strategy + risk + execution loop               |
| `trading-redis`    | `redis:7-alpine`      | Pub/sub between engine, backend, monitoring    |
| `trading-duckdb`   | `alpine:3.20`         | Owns the `/data` volume holding `market.duckdb` |
| `ollama` (ext.)    | unraid app            | Local LLM runtime, used by `research.llm`      |
| `hermes` (ext.)    | unraid app            | Internal helper service                        |

`docker-compose.yml` declares `trading-net` as `external: true` so the
existing `ollama` / `hermes` containers stay attached across rebuilds.

## Hostnames inside `trading-net`

| Service          | Address                          |
|------------------|----------------------------------|
| frontend → API   | `http://backend:8000`            |
| backend → redis  | `redis://redis:6379/0`           |
| backend → DB     | `/data/market.duckdb` (volume)   |
| any → LLM        | `http://ollama:11434`            |

Containers must address each other by name. `localhost` is forbidden inside
containers.

## Volumes

| Volume                  | Mounted at | Used by                          |
|-------------------------|-----------|----------------------------------|
| `trading-duckdb-data`   | `/data`   | backend, trading-engine, duckdb  |

## Environment variables

Defined in `.env` (example: `.env.example`). Required:

| Variable               | Notes                                            |
|------------------------|--------------------------------------------------|
| `ENV`                  | `dev`, `staging`, or `prod`                      |
| `DUCKDB_PATH`          | path inside container (`/data/market.duckdb`)    |
| `REDIS_URL`            | `redis://redis:6379/0`                           |
| `NEXT_PUBLIC_API_URL`  | `http://backend:8000`                            |
| `OLLAMA_HOST`          | `http://ollama:11434`                            |
| `OLLAMA_MODEL`         | e.g. `llama3.1:8b-instruct`                      |
| `BINANCE_API_*`        | optional; sandbox/testnet by default             |
| `COINBASE_API_*`       | optional; sandbox by default                     |

Secrets are injected via `.env`, never baked into images. See
[`.cursor/rules/security.mdc`](../.cursor/rules/security.mdc).

## Boot order

`docker compose up -d` brings services up in this order:

1. `redis` (waits for healthcheck)
2. `duckdb` sidecar (creates the volume)
3. `backend` (depends on redis healthy)
4. `trading-engine` (depends on backend started)
5. `frontend` (depends on backend started)

## Health

- `GET http://localhost:8000/api/system/health` returns
  `{status, version, env, uptime_s, db_ok, redis_ok}`.
- Frontend `/health` page renders the same data plus risk / exposure metrics.
