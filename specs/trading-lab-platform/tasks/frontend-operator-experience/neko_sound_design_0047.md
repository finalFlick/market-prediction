# FEATURE-0047: Neko sound design (SFX, royalty-free)

## Parent Epic

frontend-operator-experience

## Status

Proposed (follow-up to FEATURE-0045)

## Summary

Add optional, muted UI sounds (paw tap, success chime, error thud) with **royalty-free** or original assets, user-toggleable, default off, and `prefers-reduced-motion` / accessibility respected.

## Why

Reinforces brand without distracting operators; must not mask alerts or risk feedback.

## What

- Source + license files under `public/neko/sounds/`.
- Client-only opt-in via config / local storage; no autoplay on first load.

## Validation

- License evidence in `public/neko/README.md` and PR description; no new deps without `library-research.mdc` evidence.
