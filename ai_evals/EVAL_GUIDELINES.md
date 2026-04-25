# EVAL_GUIDELINES

How prompts and LLM outputs are evaluated. Tools: **promptfoo** (declarative
YAML, free-form output) and **deepeval** (pytest-style structural assertions).
Both run in CI; neither requires a live LLM by default.

## What gets evaluated

Every prompt registered in [`research/llm/prompts.py`](../research/llm/prompts.py):

| Prompt                | Eval focus                                                  |
|-----------------------|-------------------------------------------------------------|
| `signal_hypothesis`   | JSON shape (`name`, `intuition`, `timeframe`, `expected_horizon`, `falsification`); no "deploy" language |
| `strategy_analysis`   | JSON shape (`weaknesses`, `leakage_risks`, `ablations`); never recommends going live; flags leakage |
| `model_reasoning`     | Word budget (≤ 200); references at least one feature name; no certainty claims |

Add a new prompt → add a new test file under `ai_evals/deepeval/` and a
new entry in `ai_evals/promptfoo/promptfooconfig.yaml`. Prompts without
evals do not ship.

## Offline vs online

- Default: **offline**. `OFFLINE_LLM=true` makes deepeval read from
  `ai_evals/fixtures/offline_responses.json` and promptfoo use the JS
  provider in `promptfoo/providers/offline_provider.js`.
- CI runs offline only — eval pipelines must never depend on a reachable
  Ollama.
- Local online run: `OFFLINE_LLM=false promptfoo eval` or
  `OFFLINE_LLM=false pytest -q ai_evals/deepeval`.

## Authoring rules

1. **Every prompt is versioned.** `Prompt(name, version, system, template)`
   in `research/llm/prompts.py`. Bumping `version` is mandatory if the
   template changes.
2. **Every assertion is regression-protected.** Add the assertion to both
   layers (deepeval + promptfoo) when it's a hard requirement.
3. **Forbidden phrases are enforced.** `deploy live`, `go live`,
   `ship to production`, `definitely`, `guaranteed`, etc. — the canonical
   list lives in the test files.
4. **No real keys in fixtures.** Fixture responses are author-written or
   manually scrubbed; CI runs `gitleaks` over the whole repo.

## Tools / commands

```bash
pytest -q ai_evals/deepeval                 # contract tests (offline)
cd ai_evals/promptfoo && promptfoo eval --no-cache   # offline by default
OFFLINE_LLM=false promptfoo eval            # opt-in: hits local Ollama
```

## What the LLM is never trusted with

- Order placement, sizing, or risk approval. LLMs are research-only.
- Mutating `configs/risk.yaml` or `risk/limits.py` defaults.
- Promoting a strategy to `paper` or `live`.

See [`.cursor/rules/llm-usage.mdc`](../.cursor/rules/llm-usage.mdc) for the
full policy and the runtime enforcement test in
[`tests/security/test_llm_isolation.py`](../tests/security/test_llm_isolation.py).
