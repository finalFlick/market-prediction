# FEATURE-0049: Neko achievement badges (rules + persistence)

## Parent Epic

frontend-operator-experience

## Status

Proposed (follow-up to FEATURE-0045)

## Summary

`NekoAchievementBadge` is **display-only** in FEATURE-0045. This feature adds server-backed or local-persisted achievement events, idempotent rules, and operator-visible history — **no** live trading or capital promotion side effects.

## Why

Playful progress signals for long research cycles, without conflating gamification with PnL or risk.

## What

- Rule engine (config-driven) keyed off existing audit/run facts.
- API read surfaces + optional write path behind auth (separate from trading APIs).

## Validation

- `tests/e2e` and security tests: achievements cannot call `execution/` or bypass `risk/`.
