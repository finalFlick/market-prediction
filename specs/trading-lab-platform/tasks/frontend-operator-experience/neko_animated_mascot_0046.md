# FEATURE-0046: Neko animated mascot (designer + motion)

## Parent Epic

frontend-operator-experience

## Status

Proposed (follow-up to FEATURE-0045)

## Summary

Replace text-only ASCII mascot files with a character sheet, optional SVG, and evaluated motion (CSS-only vs `framer-motion` per design review and dependency research). **Library research** required before new runtime deps; pin versions.

## Why

Static ASCII is MVP-0 friendly; a cohesive animated Neko increases brand recall without bloating the critical path.

## What

- Export-friendly mascot asset(s) in `public/neko/mascot/` (license: CC0 / original work).
- Optional expression cycling tied to `NekoMascot` state prop; respect `prefers-reduced-motion`.

## Validation

- Styleguide or identity demo page entry once FEATURE-0034 harness is unblocked; no impact on `risk/` or `execution/`.
