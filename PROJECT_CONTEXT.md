# PROJECT_CONTEXT

> **Read this first.** Everything else is a deeper layer on top of this file.

## What this is

**Project:** AI Quant Trading Lab (`trading-lab`).

**Purpose:** A quantitative trading research platform that discovers signals,
backtests strategies, and deploys automated trading systems with strict,
deterministic risk management.

## Key goals

- Discover trading signals.
- Validate them with realistic backtests (fees, slippage, latency).
- Deploy validated strategies as automated bots — never bypassing risk.

## Pipeline (one-way, no shortcuts)

```
market_data
  → feature_engineering
    → signal_models
      → strategy_engine
        → risk_engine
          → execution
            → monitoring
```

Each stage is one Python package with a stable input/output contract.
Cross-stage shortcuts (e.g. a strategy calling the broker directly) are
**not allowed**. See `.cursor/rules/architecture.mdc`.

## Where to look

| Question                              | Read                                        |
|---------------------------------------|---------------------------------------------|
| How do I run it?                      | [`RUNNING.md`](RUNNING.md)                  |
| How do I work on it?                  | [`WORKFLOW.md`](WORKFLOW.md)                |
| What is the tech stack?               | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| What does the data look like?         | [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md)  |
| What rules govern my code?            | [`docs/CODING_STANDARDS.md`](docs/CODING_STANDARDS.md) |
| When can a strategy go live?          | [`docs/EVALUATION.md`](docs/EVALUATION.md)  |
| What are the risk limits?             | [`docs/RISK_POLICY.md`](docs/RISK_POLICY.md) |
| Who owns each pipeline stage?         | [`AGENTS.md`](AGENTS.md)                    |
| Full system design                    | [`docs/DESIGN.md`](docs/DESIGN.md)          |
| Cursor rules (always-on guidance)     | [`.cursor/rules/`](.cursor/rules)           |

## Hard rules (do not violate)

1. **Risk is non-bypassable.** Every order — backtest, paper, or live —
   passes through `risk.engine.RiskEngine.check_and_size`.
2. **No look-ahead.** Features are point-in-time. Validate with
   `research.features.validation.assert_no_lookahead`.
3. **LLMs are research-only.** No module under `execution/` may import
   `research.llm`. CI enforces this.
4. **Never commit secrets.** Use environment variables; `.env` is ignored.
5. **A task is not done until tests pass.** See `WORKFLOW.md`.
