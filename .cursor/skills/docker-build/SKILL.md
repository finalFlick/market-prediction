---
name: docker-build
description: Build, boot, and smoke-test the trading-lab docker stack. Use this skill when the user asks to build the containers, validate compose, or troubleshoot a service that won't come up.
---

# docker-build

## When to use

- After a change to a `Dockerfile`, `docker-compose.yml`, or
  `requirements`/`pyproject.toml`.
- "Bring up the stack" / "rebuild the trading engine container".
- A service is unhealthy and the user wants triage.

## Procedure

1. **Confirm the network exists.**
   ```bash
   docker network inspect trading-net >$null 2>&1; if (-not $?) { docker network create trading-net }
   ```
2. **Build images.**
   ```bash
   docker compose build trading-engine backend frontend
   ```
   If a build fails, surface the error verbatim — do not retry blindly.
3. **Boot in detached mode.**
   ```bash
   docker compose up -d
   ```
4. **Health-check loop** (≤ 30s):
   - `docker compose ps` — all services should be `running` or `healthy`.
   - `curl http://localhost:8000/api/system/health` — expect `{"status":"ok",...}`.
   - `curl http://localhost:3000` — expect a 200 with the dashboard HTML.
5. **Logs.** If anything is unhealthy:
   ```bash
   docker compose logs --tail 100 <service>
   ```
   Pipe through `Select-String -NotMatch "INFO"` to focus on warnings/errors.
6. **Tear down (optional).** `docker compose down` (keeps volumes).
   `docker compose down -v` only on user request — destroys DuckDB data.

## Outputs

- A 5-line health summary table (service / status / latest log line).
- If any service failed, the failing log excerpt and the proposed fix.

## Forbidden

- Running `docker compose down -v` without user confirmation — wipes
  market data.
- Editing `.env` to "make it work". Prefer documenting the missing var
  and asking the user.
- Building images as `root` (Dockerfiles already drop privilege).
- Pushing images to a registry from this skill.
