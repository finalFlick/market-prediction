# ai_evals

Evaluation harness for the prompts and LLM-derived outputs that live in
`research/llm/`. CI runs everything here in **offline mode** so the
pipeline never depends on a reachable Ollama instance.

## Layout

```
ai_evals/
  promptfoo/        # promptfoo configs (declarative assertions)
  deepeval/         # pytest-style structured / behavioral tests
  prompts/          # rendered prompt fixtures (golden inputs)
  fixtures/         # synthetic backtest reports, signal lists, etc.
```

## Run locally

```bash
# Python contract tests (fast, no LLM needed)
pytest -q ai_evals/deepeval

# Promptfoo declarative evals (offline, uses fixture responses)
cd ai_evals/promptfoo && promptfoo eval --no-cache

# Online run (optional, hits the local Ollama)
OFFLINE_LLM=false promptfoo eval
```

Two evaluation styles are intentional:

- **deepeval** runs as part of the regular `pytest` graph and asserts
  structural invariants (no recommendations to deploy live capital, JSON
  shape, refusal of unsafe instructions). These run in CI on every PR.
- **promptfoo** runs the prompts against either a local Ollama or a
  recorded fixture and checks free-form quality with regex / contains
  assertions. Reports are uploaded as CI artifacts.
