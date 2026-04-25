# Security

## Secrets

- Never commit real API keys, signing secrets, passwords, or tokens.
- Copy [`.env.example`](../.env.example) to `.env` (gitignored) and fill values at deploy time.
- CI runs [Gitleaks](https://github.com/gitleaks/gitleaks) on every push and PR (see `.github/workflows/ci.yml`).
- Local scan: `gitleaks detect --source . --verbose` (requires [gitleaks](https://github.com/gitleaks/gitleaks) on PATH).

## Required environment variables (reference)

| Variable | Purpose |
|----------|---------|
| `BINANCE_API_KEY` / `BINANCE_API_SECRET` | Binance REST / WS (testnet first) |
| `COINBASE_API_KEY` / `COINBASE_API_SECRET` | Coinbase Advanced Trade |
| `DUCKDB_PATH` | Embedded database file |
| `REDIS_URL` | Redis Streams transport |
| `OLLAMA_HOST` / `OLLAMA_MODEL` | Local LLM (research only) |
| `NEXTAUTH_SECRET` / `NEXTAUTH_URL` | NextAuth session signing |
| `OPERATOR_API_KEY` | Mutating / kill-switch API auth (MVP-0) |

## Trading path

- Every order — backtest, paper, or live — passes through `risk.engine.RiskEngine.check_and_size`. There is no bypass.
- `execution/` must not import `research.llm` (enforced by `tests/security/test_llm_isolation.py`).

## Further reading

- [`.cursor/rules/security.mdc`](../.cursor/rules/security.mdc)
- [docs/RISK_POLICY.md](RISK_POLICY.md)
