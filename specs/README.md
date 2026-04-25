# `specs/` — Kiro-style spec sessions

This directory holds **feature and bugfix specs** that drive the
project's structured development workflow. The system is modeled on
[Kiro IDE](https://kiro.dev/docs/specs/)'s spec-driven development
(SDD) workflow but is implemented natively in Cursor — using rules,
hooks, and a small Node scaffolder rather than a custom IDE feature.

For the canonical protocol the agent follows, read
[`.cursor/rules/spec-sessions.mdc`](../.cursor/rules/spec-sessions.mdc).
For the file-format rules applied while editing anything in this
directory, read [`.cursor/rules/spec-format.mdc`](../.cursor/rules/spec-format.mdc).

---

## What is a spec session?

A spec session is a structured exchange between you and the AI
agent that produces three durable artifacts before any code is
written:

| Phase | Artifact | Purpose |
|-------|----------------------------|--------------------------------------------|
| 1 | `requirements.md` (or `bugfix.md`) | What we're building, in EARS notation |
| 2 | `design.md` | How we'll build it |
| 3 | `tasks.md` | Two-level, traceable checklist of coding tasks |

Each phase requires **explicit approval** before the next one starts.
The agent will switch the IDE to **plan mode** during phases 1 and 2
and back to **agent mode** for phase 3 (writing code from `tasks.md`).

---

## Auto-detection

You don't need to ask for a spec session — the agent enters one
automatically when you describe a multi-file feature, a structural
refactor, an architecture change, or a non-trivial bug. The detection
rules live in `.cursor/rules/spec-sessions.mdc`.

If you want to be explicit, any of these prompts will trigger one:

- *"Build a feature to …"*
- *"Design a system that …"*
- *"Run a spec session for …"*
- *"Refactor X across modules"*

If the agent enters spec mode and you don't want it (e.g. it's
actually a one-line fix), say *"skip the spec, just do it"* and it
will drop the protocol.

---

## Manual scaffolding

You can also scaffold a spec yourself:

```bash
# Feature spec
node .cursor/scripts/spec-new.js binance-orderbook-ingest

# Bug spec
node .cursor/scripts/spec-new.js fix-paper-broker-fills --bugfix
```

Names must be kebab-case (`a-z`, `0-9`, hyphens). The script will
refuse to overwrite an existing folder.

---

## Layout of a spec folder

```text
specs/
  binance-orderbook-ingest/
    requirements.md       # Phase 1 — EARS-formatted user stories
    design.md             # Phase 2 — architecture, components, data, API
    tasks.md              # Phase 3 — two-level checklist with traceability
    notes.md              # optional — running notes during impl
    decisions.md          # optional — ADR-style decisions for this feature
```

Bug specs replace `requirements.md` with `bugfix.md`:

```text
specs/
  fix-paper-broker-fills/
    bugfix.md             # Phase 1 — current vs expected behavior, repro
    design.md             # Phase 2 — fix approach + blast radius
    tasks.md              # Phase 3 — includes a regression-test task
```

---

## EARS notation (acceptance criteria)

Every acceptance criterion in `requirements.md` and every "expected
behavior" line in `bugfix.md` uses EARS — Easy Approach to
Requirements Syntax. There are five patterns:

| Pattern | Form |
|------------------|----------------------------------------------------------|
| Ubiquitous | `THE SYSTEM SHALL <action>.` |
| Event-driven | `WHEN <trigger> THE SYSTEM SHALL <action>.` |
| State-driven | `WHILE <state> THE SYSTEM SHALL <action>.` |
| Conditional | `IF <condition> THEN THE SYSTEM SHALL <action>.` |
| Contextual | `WHERE <context> THE SYSTEM SHALL <action>.` |

This makes every requirement testable and unambiguous.

---

## Task traceability

Every leaf task in `tasks.md` ends with a `_Requirements:_` line
citing the requirement IDs it implements:

```markdown
- [ ] 2.1 Implement Binance REST historical klines client
  - Create `data/ingest/binance.py` with `fetch_klines(...)`.
  - Validate response with pydantic models.
  - Unit tests in `tests/data/test_binance_ingest.py`.
  - _Requirements: 1.1, 1.2, 3.1_
```

This is the same pattern used in regulated industries (medical,
finance, aerospace) to prove code meets its specification.

---

## Status legend

In `tasks.md`:

- `- [ ]` — not started
- `- [~]` — in progress
- `- [x]` — complete (tests pass + acceptance criteria met)

The agent updates these as it works through the plan.

---

## Relationship to existing project workflows

Spec sessions are for **structural** features and bugs:

- A new module / package / API / dashboard page → spec session.
- A new ingest source, broker adapter, or risk check → spec session.
- A non-trivial bug whose fix touches more than one file → spec
  session in `--bugfix` mode.

Spec sessions are **NOT** for:

- New trading-signal hypotheses → those use `SIGNALS.md` and the
  research-loop in [`.cursor/rules/research-workflow.mdc`](../.cursor/rules/research-workflow.mdc).
- Single-file edits, lint fixes, doc tweaks → just do them.
- Read-only investigation → just do it (or use plan mode).
- Light multi-file plans → delegate to the `planner` subagent
  ([`.cursor/agents/planner.md`](../.cursor/agents/planner.md)).
  Spec sessions exist for work big enough that the
  requirements/design/tasks artifacts will be useful weeks later.

| Scale of work | Use |
|----------------------------------------|------------------------------|
| One file, obvious change | Just do it |
| Few files, plain-English plan | `planner` subagent |
| Multi-file feature, durable artifacts | **Spec session** (this dir) |
| New trading signal hypothesis | `SIGNALS.md` row |

The architecture and security rules in
[`.cursor/rules/architecture.mdc`](../.cursor/rules/architecture.mdc),
[`.cursor/rules/coding-standards.mdc`](../.cursor/rules/coding-standards.mdc),
[`.cursor/rules/security.mdc`](../.cursor/rules/security.mdc), and
[`.cursor/rules/workflow.mdc`](../.cursor/rules/workflow.mdc) apply
to every spec — they're the constraints that requirements and
designs must respect.

---

## Components of the system

```text
.cursor/
  rules/
    spec-sessions.mdc       # alwaysApply — detection + 3-phase protocol
    spec-format.mdc         # globs:specs/**/*.md — format enforcement
  spec-templates/
    requirements-template.md
    design-template.md
    tasks-template.md
    bugfix-template.md
  hooks.json                # wires sessionStart hook
  hooks/
    spec-session-init.js    # primes every chat with spec context
  scripts/
    spec-new.js             # `node .cursor/scripts/spec-new.js <name>`

specs/                      # this directory — contains one folder per spec
  README.md                 # this file
```

---

## Tips

- **Approve aggressively.** Don't let the agent ramble — once
  requirements are clear, hit approve and move on.
- **Keep specs tight.** A good `requirements.md` is rarely longer
  than a page; a good `tasks.md` is rarely more than 30 leaf tasks.
- **Update specs as you learn.** When implementation reveals a gap,
  fix the spec first, then resume coding. The spec is the source
  of truth.
- **Specs commit with code.** Treat `specs/` like source — review,
  diff, and version it alongside the code it specifies.
