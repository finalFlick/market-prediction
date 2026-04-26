# FEATURE-0048: Neko “hacker mode” terminal (xterm.js evaluation)

## Parent Epic

frontend-operator-experience

## Status

Proposed (follow-up to FEATURE-0045)

## Summary

Optional full-screen or pane terminal aesthetic using **xterm.js** (or slimmer alt) for read-only command history and telemetry — still **no** order placement, no risk mutation, whitelist GET-only commands mirroring `NekoEasterEgg` policy.

## Why

The compact easter-egg in FEATURE-0045 is intentional scope control; a richer terminal is gated behind dependency research, bundle-size review, and security review of command surface.

## What

- `library-research.mdc` pass: pin `xterm` + addons, size budget, a11y.
- Feature flag; defaults off.

## Validation

- E2E smoke: build still green; `tests/security` unchanged for execution path; command whitelist tests if expanded.

## Note

**Achievement persistence** and award rules are **FEATURE-0049**, not this ticket.
