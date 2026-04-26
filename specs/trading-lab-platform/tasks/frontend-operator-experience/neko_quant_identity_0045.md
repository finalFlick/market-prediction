# FEATURE-0045: Neko Quant brand identity layer (MVP-0)

## Parent Epic

frontend-operator-experience

## Status

Implemented (2026-04-26) — additive identity chrome on top of Catppuccin Mocha; follow-ups FEATURE-0046–0049

## Summary

Layer the **Neko Quant** kawaii-hacker-cat brand on the operator console: terminal-style status line, voice tables, ASCII mascot states, read-only research observation card (with mandatory “not a trade signal” disclaimer), diagnostics easter-egg (GET-only), Icon set, Inter + JetBrains Mono, and Swagger `/docs` watermark. No changes to trading, risk, or order paths.

## Why

Operator trust and product personality require a single coherent brand without weakening LLM isolation or the non-bypassable risk engine.

## What (delivered in repo)

- `frontend/components/identity/*` — shell, status, mascot, loading, observation card, easter-egg, achievement badge (display-only), hand-rolled icons.
- `frontend/lib/neko-voice.ts`, `frontend/lib/ascii-candle.ts`, `frontend/styles/neko.css`, `frontend/public/neko/**`.
- `app/layout.tsx` — `NekoShell`, `next/font` Inter + JetBrains Mono, Tailwind font + keyframe extensions.
- Playful copy on **empty / non-critical** list states on tracked app routes; `health` KPI surfaces unchanged.
- `backend/api/static/swagger-trading-lab.css` — `neko@market:~$ /docs` watermark.
- Decisions **DEC-011** / **DEC-012**; `docs/UI_REQUIREMENTS.md` brand section; `.cursor/rules/neko-voice.mdc`.

## Source Traceability

- requirements.md: operator UX, LLM isolation, read-only research framing
- design.md: frontend inventory; operator console
- `DEC-010` (Catppuccin Mocha) — Neko is additive chrome, not a palette fork

## Requirements Covered (conceptual)

- Beginner-safe, trustworthy UI with clear separation of research “observations” vs trade signals
- No LLM or playful copy on risk/execution/critical error surfaces (see DEC-012)

## Validation

- `ReadLints` on touched frontend files; `ruff` / `mypy` (backend) / `pytest tests/e2e/test_api_app.py` green.
- Full `npm run build` may remain blocked if unrelated WIP frontend paths are untracked — document in SESSION_LOG if so.

## Follow-ups

- [FEATURE-0046](./neko_animated_mascot_0046.md) — SVG / motion mascot
- [FEATURE-0047](./neko_sound_design_0047.md) — royalty-free SFX
- [FEATURE-0048](./neko_hacker_mode_0048.md) — full-screen terminal / xterm.js eval
- [FEATURE-0049](./neko_achievements_0049.md) — achievement engine + persistence
