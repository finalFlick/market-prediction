# MCP integration

`.cursor/mcp.json` declares four MCP servers the agents can use during
research and review. They are **not** part of the runtime — the trading
engine never depends on them.

| Server       | What it gives an agent                                          | When to use                                                     |
|--------------|-----------------------------------------------------------------|-----------------------------------------------------------------|
| `duckdb`     | Read-only SQL over `data/market.duckdb`                         | Inspect bars, signal lifecycle, recent trades, backtest table   |
| `github`     | Issues, PRs, files, releases                                    | `babysit` flows, opening release PRs, triage                    |
| `playwright` | Browser automation                                              | Scrape exchange docs, news, blog posts as **inputs to features** |
| `ccxt`       | Unified spot/derivatives exchange API                           | Sanity-check live prices, fetch historical klines for new pairs |

## Read-only by default

- `duckdb` is started with `DUCKDB_READ_ONLY=true`. Writes happen only via
  the trading engine, not via MCP.
- `ccxt` is configured with `CCXT_SANDBOX=true`. Order placement requires
  switching to a non-sandbox config, which is intentionally not the default.
- `github` reads `GITHUB_TOKEN` from the environment so it never lands in
  this repo. Per `.cursor/rules/security.mdc`, secrets stay in env vars.

## Running

These commands assume `uv` and `npx` are on PATH. Cursor will start each
server on demand; restart Cursor after editing `.cursor/mcp.json`.

For the GitHub server set:

```bash
export GITHUB_TOKEN=ghp_…   # personal access token, scoped read-only
```

For the ccxt server, optionally set per-exchange API keys:

```bash
export BINANCE_API_KEY=…
export BINANCE_API_SECRET=…
```
