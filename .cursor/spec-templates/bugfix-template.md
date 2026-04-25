# Bugfix: {{BUG_NAME}}

<!--
This is the Kiro-style bug-spec variant. It replaces requirements.md
for a bugfix-mode session. After this is approved, write a short
design.md describing the chosen fix and a tasks.md including a
regression test.
-->

## Document Information

- **Bug Name**: {{BUG_NAME}}
- **Reported by**: {{REPORTER}}
- **Date**: {{DATE}}
- **Severity**: critical | high | medium | low
- **Affected modules**: *e.g. `risk/`, `execution/brokers/binance.py`*
- **Related Documents**:
  - Design: `./design.md`
  - Tasks: `./tasks.md`

## Summary

*One sentence describing the bug and its user-visible impact.*

---

## Current Behavior

*What is happening today, in concrete terms. Cite logs, stack
traces, screenshots, metrics, or test failures wherever possible.*

```text
{{paste relevant log line / traceback / metric / repro output}}
```

### When does it happen?

*Always | only on certain inputs | only under load | only on Windows |
only with specific config — be specific.*

### Blast radius

- *Which users / strategies / brokers / pipelines are affected.*
- *Is live capital at risk?*
- *Is the kill-switch firing or silent?*

---

## Expected Behavior

*Describe the correct behavior in EARS form so it's testable.*

1. WHEN {{trigger}} THE SYSTEM SHALL {{correct response}}.
2. IF {{condition}} THEN THE SYSTEM SHALL {{correct behavior}}.
3. WHILE {{state}} THE SYSTEM SHALL {{continuous correct behavior}}.

---

## Reproduction Steps

*Minimal repro. Ideal: a one-line pytest invocation that fails today.*

1. {{step 1}}
2. {{step 2}}
3. *Observed:* {{wrong outcome}}
4. *Expected:* {{correct outcome}}

```bash
# Smallest possible repro command
pytest tests/{{module}}/test_{{thing}}.py::test_{{case}} -q
```

---

## Root Cause Hypothesis

*Best current theory. If unknown, state what you've ruled out and
what evidence you still need. Update this section when the cause is
confirmed.*

- *Hypothesis 1: ...*
- *Hypothesis 2: ...*
- *Confirmation plan: how we will prove or disprove each.*

---

## Behavior That Must NOT Change

*Explicit anti-regressions. List the existing tests, behaviors, and
APIs whose semantics must remain identical after the fix.*

- THE SYSTEM SHALL continue to ... *(existing behavior 1)*.
- WHEN ... THE SYSTEM SHALL still ... *(existing behavior 2)*.
- *No public API signature changes in `{{module}}.{{function}}`*.
- *No change in serialized output format for `{{artifact}}`.*

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|--------------------------------|------------|--------|----------------------|
| Fix introduces new regression | low/med/high | low/med/high | regression test in tasks.md |
| Fix changes performance | low/med/high | low/med/high | perf test in tasks.md |
| Fix touches risk path | low/med/high | high | dual happy/reject test |

If the fix touches `risk/`, `execution/`, or `configs/risk.yaml`, the
PR requires human review per `security.mdc`.

---

## Affected Files / Modules

*Best estimate after a quick scan; refine during design.*

- `{{path/to/file.py}}` — {{why}}
- `{{path/to/other.py}}` — {{why}}
- `tests/{{module}}/test_{{thing}}.py` — needs a new regression test

---

## Verification Plan

*How we will know the bug is fixed and not just masked.*

- [ ] New failing test reproduces the bug pre-fix.
- [ ] Same test passes post-fix.
- [ ] Existing tests still pass (`pytest -q`).
- [ ] Lint + typecheck still pass (`ruff check .`, `mypy --strict .`).
- [ ] Logs / metrics show the corrected behavior in a smoke run.
- [ ] Anti-regression list above is verified item-by-item.

---

## Bugfix Review Checklist

Run before marking the bugfix spec approved:

- [ ] Current behavior is documented with concrete evidence
      (log, trace, metric, screenshot).
- [ ] Expected behavior is in EARS form and testable.
- [ ] At least one root-cause hypothesis is plausible.
- [ ] Anti-regression list is non-empty and specific.
- [ ] Reproduction is minimal (one command, no flake).
- [ ] Severity is justified (critical only when capital or safety
      is at risk).

---

> **Next phase:** when this document is approved, fill in
> `./design.md` (briefly — focus on the chosen fix and its blast
> radius), then `./tasks.md` from
> `.cursor/spec-templates/tasks-template.md`. The tasks list MUST
> include a regression-test task that fails before the fix and
> passes after.
