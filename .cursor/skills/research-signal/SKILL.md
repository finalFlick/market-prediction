---
name: research-signal
description: Move a signal hypothesis from idea to a tracked entry in SIGNALS.md and the signals DuckDB table. Use this skill when the user proposes a new trading idea, references a paper or article, or asks to add a signal hypothesis.
---

# research-signal

This skill should be used when the user wants to register a new signal
hypothesis. It produces a SIGNALS.md entry and a `signals` table row,
both with status `hypothesis`. **It does not write trading code.**

## When to use

- User says: "add a signal for X", "log this idea", "the paper from <author>
  suggests Y, capture it".
- An LLM-driven research session has produced a candidate.

## Inputs

- A short name for the signal (e.g. `vol-of-vol`, `funding-skew`).
- A one-paragraph intuition (what does it measure, why might it predict
  return).
- A timeframe (`1m`, `5m`, `1h`, `1d`).
- Optional: source citation, expected horizon, falsification criterion.

## Procedure

1. Read [`SIGNALS.md`](mdc:SIGNALS.md) to confirm the name is unused.
2. Read [`research/llm/prompts.py`](mdc:research/llm/prompts.py); if the user
   wants the LLM to refine the intuition, render `SIGNAL_HYPOTHESIS_V1`
   and call `research.llm.client.chat()` (research-only — do not let the
   LLM choose the signal name or timeframe).
3. Append a new section to `SIGNALS.md` with the schema documented at the
   top of that file: name, status (=`hypothesis`), timeframe, intuition,
   owner, falsification, references.
4. Insert a row into the `signals` table:
   ```python
   from data.repositories import SignalsRepo, SignalRecord
   from data.db import connect
   conn = connect()
   SignalsRepo(conn).upsert(SignalRecord(
       signal_id=<slug>, name=<name>, status="hypothesis",
       timeframe=<tf>, intuition=<intuition>, owner=<owner>,
   ))
   ```
5. Update `TODO.md` if the user has indicated they want this signal
   prioritized for `Milestone 2 — Feature pipeline` work.

## Outputs

- Updated `SIGNALS.md`.
- New row in `signals` (verifiable: `SELECT * FROM signals WHERE
  signal_id = '<slug>'`).
- Optional `TODO.md` entry under Milestone 2.

## Forbidden

- Writing trading logic in this skill. Implementation lives in
  `research/features/` and `strategies/` and is gated by separate skills.
- Calling Ollama and trusting its output verbatim. The LLM proposes —
  the human (or domain agent) decides.
- Setting `status` to anything other than `hypothesis`. Promotion happens
  via `evaluate-strategy` and `promote-strategy`.
