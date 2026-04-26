# Session Log

A reverse-chronological journal of working sessions. Each entry: date, who
(human or agent role), what was attempted, what landed, what is blocked.

Format:

```
## YYYY-MM-DD — <session title>
- **Agent**: <Research|Signal|Backtest|Strategy|Risk|Execution|Monitoring|Human>
- **Goal**: one sentence
- **Done**: bullet list of merged changes
- **Verified**: commands run + result (e.g. `pytest -q` → 12 passed)
- **Blocked / next**: bullet list
```

---

## 2026-04-26 — Styleguide Mocha rebuild (FEATURE-0034) + frontend-init

- **Agent**: Developer
- **Goal**: Land Catppuccin Mocha + Neko Quant styleguide harness and compose
  `frontend-init` per the approved styleguide Mocha rebuild plan.
- **Done**:
  - Cherry-picked `9913a86` onto local `main` (`docker-compose.dev.yml`
    `frontend-init` + `depends_on: service_completed_successfully`).
  - Branch `feat/styleguide-mocha` (tip commit): full registry (`frontend/styleguide/*`),
    demos, Vitest + jsdom shims, Mocha-classed UI components (primitives, data,
    charts, operator), `/styleguide` + `/styleguide/[componentId]`, Badge/Card
    variants, `EquityChart` empty state, `TradesTable` `live`/`paper` badges,
    `AiInsightPanel` uses `NEKO_NOT_A_TRADE_SIGNAL`; removed WIP
    `frontend/styles/tokens.css` (single palette source: Tailwind).
  - Docs: `docs/UI_REQUIREMENTS.md` registry pointer + `/styleguide` route;
    `specs/.../style_guide_component_library_0034.md` addendum; `TODO.md` conflict
    section closed.
- **Verified**:
  - `docker compose -f docker-compose.yml -f docker-compose.dev.yml config --services` →
    includes `frontend-init` (earlier).
  - `cd frontend; npm test` → 11 passed; `npm run typecheck` → clean;
    `npm run lint` → no warnings; `npm run build` → exit 0 (Next lockfile patch
    warnings only).
- **Verified (repo)**:
  - `py -3.12 -m pytest tests/cursor_harness -q` → 131 passed
  - `py -3.12 -m pytest -q -m "not slow and not integration"` → 293 passed
  - `ruff check .` → all checks passed; `mypy --strict .` → 182 files, no issues
- **Pushed (2026-04-26 15:50)**:
  - `origin/main` `df4c4d7..8792c1f` (cherry-picked `frontend-init`).
  - `origin/feat/styleguide-mocha` (new); PR URL printed by `git push`.
- **Observations / proposed rule updates**:
  - Self-referencing the current commit's own short SHA in its body / spec
    addendum forced **5 `git commit --amend`** cycles. Rule:
    branch-name-or-post-merge-SHA only.
  - PowerShell host: `&&` and heredoc commit messages do not work; the
    working recipe is `Set-Content .git\COMMIT_MSG.txt … ; git commit -F …`.
  - `lightweight-charts` cannot run under `jsdom`; tests mock the module.
  - **Ratified as DEC-014**: edits landed in `workflow.mdc` (self-SHA
    section + PowerShell recipe) and `frontend.mdc` (lightweight-charts
    jsdom subsection). Proposal file removed.
- **Blocked / next**: Owner opens / squash-merges PR for
  `feat/styleguide-mocha`. Do not delete `backup/chore-gov-pre-slim` until
  the merge lands.

## 2026-04-26 — Collided agent recovery: styleguide-ci-bootstrap-agent

### Starting context

- Resumed after parallel-agent collision. Canonical continuation source
  reviewed: `TODO.md` "Agent Coordination / Conflict Status" section and the
  most recent `SESSION_LOG.md` entries (DEC-013 ratification and Neko Quant
  FEATURE-0045 land).
- This agent's original goal:
  `.cursor/plans/styleguide_ci_base_cc26754b.plan.md` —
  TODO 1 (FEATURE-0034 full styleguide), TODO 2 (`trading-base` CI Phase 1+2),
  TODO 3 (`frontend-init` Compose service).

### Git state reviewed (read-only)

- Branch: `main` (ahead of `origin/main` by 3 — Neko + DEC-013 commits).
- Working tree: 27 untracked files under `frontend/styleguide/`,
  `frontend/components/{operator,charts,data,ui}/**`, `frontend/styles/`,
  `frontend/vitest.{config,setup}.ts`, plus 2 unrelated audit-agent files
  (`.cursor/scratchpad.md`, `.pipeline/swagger-catppuccin/run.json`). No
  modifications to tracked files.
- Stashes: one — `stash@{0}: On github-public-governance: wip-all-before-slim-pr3`.
  Inspected with `git stash show --name-only`: 16 entries, all
  modifications to pre-existing files; **no new styleguide files are in this
  stash.**
- Worktrees: single (`main` at workspace root).
- Relevant branches:
  - `backup/chore-gov-pre-slim` (local-only, audit-preserved): tip
    `07d05ab feat(frontend): full styleguide inventory ...`. Despite the
    commit subject, `git ls-tree -r 07d05ab -- frontend/styleguide
    frontend/components/{operator,charts,data} frontend/components/ui/{button,select,textarea,skeleton,empty-state,error-state}.tsx
    frontend/styles frontend/vitest.config.ts frontend/vitest.setup.ts`
    returns **empty** — only six pre-existing files were modified in that
    commit. The new component, registry, types, fixtures, demos, and tests
    are **not** in `07d05ab` or in the parent commits on that branch.
- Merged upstream via PR #3 / PR #17:
  - TODO 2 Phase 1+2 (`ci(docker): build trading-base before service images
    and publish to GHCR`) at `8174b0b`.
  - Frontend dev deps (`vitest`, `@testing-library/react`, `jsdom`,
    `@vitejs/plugin-react`) already in `frontend/package.json` on `main`.

### Recovered candidate work

| Location | Files | Status |
|---|---|---|
| Working tree (untracked) | 27 styleguide files (registry, types, demos, fixtures, vitest config + setup, all new operator/charts/data/ui components, `styles/tokens.css`) | Only copy in repo |
| `backup/chore-gov-pre-slim` @ `07d05ab` | 6 modifications to existing files (Badge variants, Card cva, EquityChart empty-state, TradesTable variant fix, app/styleguide/page.tsx rewrite, tailwind/globals updates) | Preserved on a local branch only |
| `backup/chore-gov-pre-slim` @ `9913a86` | `docker-compose.dev.yml` (+18 lines: `frontend-init` one-shot service, `frontend.depends_on` ordering) — TODO 3 from the plan | Preserved on a local branch only; never opened as a PR |
| `stash@{0}` | Same 16-file diff that `backup/chore-gov-pre-slim` already contains | Redundant with the backup branch |

Likely original goal (confirmed): execute the
`.cursor/plans/styleguide_ci_base_cc26754b.plan.md` plan end-to-end.

### Conflict findings

1. **TODO.md inaccuracy.** Today's `TODO.md` claims:
   > "These files are not lost; they exist both in the local working tree
   > and as commit `07d05ab` on `backup/chore-gov-pre-slim`."
   `git ls-tree` shows the new files are **not** in `07d05ab`. Only the
   working-tree copy preserves them. Without an explicit commit/stash, a
   `git clean -fd` or branch wipe would lose this work.
2. **Palette conflict with DEC-010 (Catppuccin Mocha).** My
   `frontend/styles/tokens.css` defines the Kitsune palette
   (`--tl-mint`, `--tl-foxfire`, `--tl-magenta`, …). `main`'s
   `frontend/tailwind.config.ts` is now verbatim Catppuccin Mocha (DEC-010);
   utility classes my components reference (`bg-mint`, `border-foxfire`,
   `text-foxfire`, `shadow-neon`, `border-live`, `border-risk`,
   `animate-pulse-live`, `ease-terminal`, `bg-magenta/15`, …) no longer
   exist on `main`. Audit-agent's prior session log already records
   `npm run typecheck` and `npm run build` failing on these files.
3. **Neko identity additivity.** FEATURE-0045 added
   `frontend/components/identity/*` — disjoint from this agent's paths,
   so no path collision; only the palette layer needs reconciliation.

### Decision

**Strategy: Option B — Preserve But Do Not Resume.**

Reasons:
- The styleguide WIP is real, useful work, but landing it as-is breaks the
  current canonical palette (DEC-010) and is already known to break
  `typecheck` / `build`. A rebase against Catppuccin Mocha tokens is
  required before this can land.
- `TODO.md` already classifies resumption as `[!]` decision blocker,
  human-only.
- This agent's hard guardrails forbid committing without explicit
  instruction.
- The other two plan items already landed via PR #17 and are preserved on
  `backup/chore-gov-pre-slim` (`9913a86` for `frontend-init`).

### Changes made (this session, recovery only — no code edits)

- `SESSION_LOG.md` (this entry).
- `TODO.md`: corrected the inaccurate "files exist on `07d05ab`" claim and
  flagged the DEC-010 palette rebase as a precondition.
- `specs/.../style_guide_component_library_0034.md`: small implementation
  addendum recording the recovery state and rebase requirement.

### Changes intentionally skipped

- No edits to any untracked styleguide file. Working-tree contents
  preserved exactly as found.
- No `git commit`, `git stash pop`, `git stash drop`, `git branch -D`,
  `git reset --hard`, or `git push`.
- No attempt to apply `stash@{0}` (already redundant with the backup
  branch).
- No new recovery branch — `git switch -c` would not durably persist the
  untracked files without a commit, and committing is not authorised by
  the prompt.

### Remaining handoff

Decision needed from the user (one of):

1. **Cherry-pick + rebase.** Cherry-pick `9913a86` (`frontend-init`) into a
   small PR. Separately, manually port the 27 working-tree files into a
   `feat/styleguide-mocha-rebase` branch with all tokens / utilities
   rewritten against the Catppuccin Mocha palette in
   `frontend/tailwind.config.ts` and the Neko keyframes. Owner-only PR.
2. **Retire and start fresh from FEATURE-0034 design tokens table.** Drop
   the working-tree copy, drop `backup/chore-gov-pre-slim`, and rebuild
   only the registry/types/fixtures + a smaller initial component slate
   that already targets Mocha. Smaller blast radius, no rebase debt.
3. **Defer.** Leave files in the working tree (or commit them to a
   `wip/styleguide-kitsune-snapshot` branch) and revisit after MVP-0
   ships. Audit-agent's existing `[!]` flag stays.

Until the user picks one, do not run `git clean`, do not delete
`backup/chore-gov-pre-slim`, and do not pop `stash@{0}` — the
working-tree styleguide WIP is the only copy of the new files.

---

## 2026-04-26 — DEC-013 + Cursor rules (spec addenda, feature id check, local fonts)

- **Agent**: Developer
- **Goal**: Ratify the proposal in
  `.cursor/state/proposed/2026-04-26-additive-feature-addenda-and-font-fallback.md`
  by editing `spec-sessions.mdc`, `spec-format.mdc`, `frontend.mdc`, and
  `DECISIONS.md` (DEC-013); remove the proposal file.
- **Done**: `spec-sessions.mdc`, `spec-format.mdc`, `frontend.mdc` + **DEC-013** in
  `DECISIONS.md`; proposal file removed. (See latest `main` for commit.)
- **Verified**: n/a (markdown only).
- **Blocked / next**: none.

## 2026-04-26 — Neko Quant identity layer (FEATURE-0045, DEC-011/012)

- **Agent**: Developer
- **Goal**: Ship additive Neko Quant brand chrome (identity components, voice,
  fonts, Swagger watermark, decisions/docs/tickets) without editing paused
  styleguide WIP paths.
- **Done**:
  - `frontend/components/identity/*` — `NekoShell`, `NekoStatus`, `NekoMascot`,
    `NekoLoading`, `NekoObservationCard`, `NekoEasterEgg`, `NekoAchievementBadge`,
    `neko-icons`.
  - `frontend/lib/neko-voice.ts`, `frontend/lib/ascii-candle.ts`, `formatPawConfidence`
    in `frontend/lib/utils.ts`, `frontend/styles/neko.css`, `public/neko/**`.
  - `frontend/app/layout.tsx` — Inter + JetBrains Mono (`next/font/google`),
    `NekoShell` wrap, Tailwind font + `paw-bounce` / `scanline` / `candle-pulse`.
  - Voice on empty / playful surfaces on tracked `app/**/page` routes; health KPIs
    unchanged. Trades: empty state uses Neko copy without editing `trades-table`.
  - `backend/api/static/swagger-trading-lab.css` — `neko@market` `/docs` watermark.
  - Specs: FEATURE-0045..0049, epic + `tasks.md` index; FEATURE-0034 addendum;
    `.cursor/rules/neko-voice.mdc`, `docs/UI_REQUIREMENTS.md` brand section,
    `DECISIONS.md` DEC-011/012, `README` tagline, `TODO.md` note.
- **Verified**:
  - `py -3.12 -m pytest tests/e2e/test_api_app.py -q` → 9 passed
  - `py -3.12 -m ruff check .` → All checks passed
  - `py -3.12 -m mypy --strict .` → Success, 182 source files
  - `cd frontend; npm run lint` → No ESLint warnings or errors
  - `ReadLints` (identity + layout + neko-voice + utils) → clean
- **Deferred / blocked**:
  - `npm run typecheck` / `npm run build` fail on pre-existing WIP under
    `styleguide/`, `components/operator/`, and related Badge variant typings —
    not introduced by this session (same class of blocker as paused styleguide
    agent). `next build` also emitted lockfile patch warnings in this
    environment; production build of WIP tree remains a follow-up when
    FEATURE-0034 lands.

## Session: 2026-04-26 — Adopt Catppuccin Mocha as project palette (DEC-010)

- **Agent**: Orchestrator (autonomous /orchestrate, single iteration)
- **Goal**: Replace the in-house Kitsune palette with verbatim Catppuccin
  Mocha hex values across `/docs` and the dashboard, per user direction
  *"Just match the online palette dont use our custom colors"*.
- **Done**:
  - `frontend/tailwind.config.ts` — replaced Kitsune tokens with raw
    Catppuccin Mocha names (`base`, `mantle`, `crust`, `surface0/1/2`,
    `overlay0/1/2`, `text`, `subtext0/1`, all 14 accents); added
    semantic role aliases (`primary → blue`, `success → green`,
    `warning → yellow`, `danger → red`, `card → surface0`,
    `border → surface2`, `muted → surface1`, `muted-foreground →
    subtext0`, `background → base`, `foreground → text`,
    `primary-foreground → crust`).
  - [`frontend/app/globals.css`](frontend/app/globals.css) — body bg
    `#1e1e2e`, color `#cdd6f4`, selection `#585b70`.
  - [`backend/api/static/swagger-trading-lab.css`](backend/api/static/swagger-trading-lab.css)
    — rewritten with verbatim Mocha hex; HTTP methods mapped GET=Blue,
    POST=Green, PUT=Peach, PATCH=Mauve, DELETE=Red.
  - [`docs/UI_REQUIREMENTS.md`](docs/UI_REQUIREMENTS.md) — Visual
    rules and Status colors sections rewritten to reference Catppuccin
    Mocha + the upstream
    [style guide](https://github.com/catppuccin/catppuccin/blob/main/docs/style-guide.md).
  - [FEATURE-0034](specs/trading-lab-platform/tasks/frontend-operator-experience/style_guide_component_library_0034.md)
    — Design Direction mood line changed from "neon telemetry over a
    black-glass trading console" to "quiet operator console with a
    coherent accent vocabulary"; Design Tokens table lists raw Catppuccin
    names with hex values.
  - [`DECISIONS.md`](DECISIONS.md) — new **DEC-010** records the palette
    adoption, license attribution, role-mapping, and reversibility.
  - `.pipeline/swagger-catppuccin/run.json` — orchestrator run log
    (per-task acceptance checks + verification evidence).
  - `.cursor/scratchpad.md` — current state summary.
  - `.gitignore` — added `.pipeline/` and `.cursor/scratchpad.md` so
    orchestrator runtime artifacts stay out of commits.
- **Verified**:
  - `py -3.12 -m ruff check backend/api/app.py tests/e2e/test_api_app.py`
    → all checks passed
  - `py -3.12 -m mypy --strict backend/api/app.py tests/e2e/test_api_app.py`
    → success: no issues found in 2 source files
  - `py -3.12 -m pytest tests/e2e/test_api_app.py -q` →
    **9 passed in 8.38 s** (includes
    `test_swagger_docs_serves_themed_html` and
    `test_swagger_theme_css_is_served`)
  - `ReadLints` on all six modified files → no linter errors
- **Sources cited** (per `.cursor/rules/library-research.mdc`):
  - [Catppuccin palette JSON](https://raw.githubusercontent.com/catppuccin/palette/main/palette.json)
    v1.8.0 (MIT)
  - [Catppuccin style guide](https://github.com/catppuccin/catppuccin/blob/main/docs/style-guide.md)
    — role mapping (Blue=primary/links, Green=success, Yellow=warning,
    Red=errors, Mauve=Mark2/keywords, Lavender=active border,
    Teal=color6/cyan)
  - Compared against [Amoenus/SwaggerDark](https://github.com/Amoenus/SwaggerDark)
    (191⭐, MIT, generic dark) and
    [Itz-fork/Fastapi-Swagger-UI-Dark](https://github.com/Itz-fork/Fastapi-Swagger-UI-Dark)
    (29⭐, MIT, Catppuccin-based but pinned to Swagger UI 4.x);
    decided to inline the palette rather than vendor either.
- **Blocked / next**:
  - Paused-styleguide-agent WIP on `backup/chore-gov-pre-slim`
    (`07d05ab`) defines `frontend/styles/tokens.css` against the OLD
    Kitsune palette and will conflict on land. That branch needs a
    rebase to consume DEC-010 tokens. Documented in DEC-010
    consequences.
  - `/redoc` is still default-light. Out of scope; follow-up if
    desired.
  - No git commit made; awaiting user instruction.

---

## Session: 2026-04-26 — Collided Agent Recovery: swagger-docs-styleguide-agent

### Starting Context

- Resumed after parallel-agent collision. Three agents were active 2026-04-26:
  the audit/governance agent (PR #3, PR #17), a paused frontend-styleguide
  agent (FEATURE-0034 WIP, captured on `backup/chore-gov-pre-slim`), and
  this Swagger-docs theming agent.
- Canonical continuation source reviewed: `TODO.md` (2026-04-26 status
  addendum + Agent Coordination block) and the latest `SESSION_LOG.md`
  audit entry.
- This recovery does not touch the paused styleguide agent's WIP files
  (all under `frontend/`); scope is strictly `backend/api/` chrome.

### Git State Reviewed

- Branch: `main`, in sync with `origin/main` at `df4c4d7`.
- Working tree: 18 untracked frontend files (paused-agent FEATURE-0034 WIP).
- Stashes: `stash@{0} wip-all-before-slim-pr3` — paused-agent content,
  redundant with `backup/chore-gov-pre-slim`. Not touched.
- Worktrees: none (only `main` checked out).
- Relevant branches: `main`, `backup/chore-gov-pre-slim` (held).
- `git log --all -- backend/api/app.py backend/api/static
  tests/e2e/test_api_app.py` confirms the prior Swagger work was never
  committed to any branch or stash.

### Recovered Candidate Work

- Location: never committed; lived only as live working-tree edits during
  the prior session and was discarded (most likely caught in a `git
  restore` / housekeeping operation after the audit agent finished its
  governance + CI work).
- Files that had been modified pre-revert: `backend/api/app.py`,
  `backend/api/static/swagger-trading-lab.css` (new),
  `tests/e2e/test_api_app.py`, `RUNNING.md`, `SESSION_LOG.md`,
  `specs/trading-lab-platform/tasks.md`,
  `specs/trading-lab-platform/tasks/frontend-operator-experience/style_guide_component_library_0034.md`.
- Likely original goal: theme FastAPI `/docs` (Swagger UI) to match the
  operator-console palette in `frontend/tailwind.config.ts`
  (FEATURE-0034 design direction).
- Documentation footprints that survived the revert and now describe
  nonexistent code: the prior 2026-04-26 *"Swagger /docs themed to
  operator styleguide"* SESSION_LOG entry (below), the
  `RUNNING.md` themed-`/docs` row, and the `tasks.md`
  *"Addendum: OpenAPI Swagger UI themed to operator console"* block.
- Still relevant? **yes** — the user explicitly requested the theme and
  asked the prior agent to fix the visual regression it caused.
- Conflict risk: **low** — backend-only, no overlap with the paused
  styleguide agent's frontend WIP, no overlap with `main`.

### Decision

- **Strategy: Resume Work (Option A) — conservative re-apply.**
- Reason: stale "claim of success" docs already exist; the cheapest path
  back to internal consistency is to make the implementation match those
  claims, with the visual bug fix from the previous session baked in.
- The previous attempt failed visually because it passed
  `swagger_css_url=` to `get_swagger_ui_html`, which **replaces** the
  default Swagger UI CDN base stylesheet. The corrected approach used
  here renders Swagger UI with all defaults and post-processes the HTML
  to inject the override `<link>` just before `</head>`, so the base
  layout/typography stays intact and only colors/borders/typography
  cascade on top.

### Changes Made

- Re-created
  [`backend/api/static/swagger-trading-lab.css`](backend/api/static/swagger-trading-lab.css)
  with `.swagger-ui` color/border/typography overrides synced to
  `frontend/tailwind.config.ts` extend.colors. Top-of-file comment
  records the sync requirement.
- Updated
  [`backend/api/app.py`](backend/api/app.py): `docs_url=None`,
  `StaticFiles` mount on `/static`, custom `GET /docs` route that calls
  `get_swagger_ui_html(...)` with defaults (no `swagger_css_url=`) plus
  `swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"}`, then
  injects the override stylesheet `<link>` before `</head>`. The route
  is `include_in_schema=False`. Also coerced `base.body` through
  `bytes(...)` to satisfy `mypy --strict` against
  `bytes | memoryview[int]`.
- Re-added two e2e tests in
  [`tests/e2e/test_api_app.py`](tests/e2e/test_api_app.py):
  `test_swagger_docs_serves_themed_html` (asserts 200, `swagger-ui` in
  body, **`swagger-ui-dist` CDN reference still present** — guard
  against the prior visual regression — and our `_SWAGGER_CSS_URL`
  appended) and `test_swagger_theme_css_is_served` (asserts 200,
  `text/css`, `.swagger-ui` content).
- Re-added the *"Implementation addendum (2026-04-26): API docs chrome"*
  block to
  [`specs/trading-lab-platform/tasks/frontend-operator-experience/style_guide_component_library_0034.md`](specs/trading-lab-platform/tasks/frontend-operator-experience/style_guide_component_library_0034.md);
  this block had also been reverted along with the code.
- The
  [`specs/trading-lab-platform/tasks.md`](specs/trading-lab-platform/tasks.md)
  *"Addendum: OpenAPI Swagger UI themed to operator console (2026-04-26)"*
  block survived the revert and now correctly describes existing code
  again — left untouched.

### Verified

- `py -3.12 -m ruff check backend/api/app.py tests/e2e/test_api_app.py`
  → all checks passed.
- `py -3.12 -m mypy --strict backend/api/app.py tests/e2e/test_api_app.py`
  → success: no issues found in 2 source files.
- `ReadLints` on the three changed files → no linter errors.
- Code review of the route: `get_swagger_ui_html(...)` called with
  defaults emits the standard CDN `<link>` for swagger-ui-dist@5; the
  `.replace("</head>", '<link ... swagger-trading-lab.css"></head>', 1)`
  injection runs once and adds the override after the base CSS in source
  order, so both stylesheets load and ours wins on cascade.

### Verification Gap (must be re-run by the user)

- **`pytest` is currently blocked on this Windows session** by a hung
  WMI service. Repro signal: `py -3.12 -X faulthandler -c "import
  platform; platform.system()"` triggers `_wmi_query` and never returns;
  the import chain `runs.orchestrator → backtests/__init__ →
  backtests/engine → vectorbt → ipywidgets → IPython.terminal →
  IPython.core.kitty → platform.win32_ver` therefore wedges every
  pytest collection that touches `backend.api.app`.
- Root cause is **environmental, not code**: aggressive
  `Get-Process | Stop-Process -Force` calls during the prior session
  appear to have left the WMI provider in a bad state. Restoring it
  requires either a Windows session restart or, from an **elevated**
  PowerShell, `Restart-Service Winmgmt -Force`.
- After WMI recovers, the user (or any future agent) should run, in
  this order, to validate this resume:
  - `py -3.12 -m pytest tests/e2e/test_api_app.py -q` — expects 9 passed.
  - `py -3.12 -m pytest -q` — expects ~294 passed (the run captured by
    the prior session before it lost the work).
  - `py -3.12 -m ruff check .`
  - `py -3.12 -m mypy --strict --explicit-package-bases backend`
- The prior 2026-04-26 *"Swagger /docs themed to operator styleguide"*
  SESSION_LOG entry below cites `pytest -q → 294 passed`; that
  verification is **stale relative to the current tree** (the code it
  validated was reverted shortly after). The current code has been
  reconstructed to match the same intent and passes static analysis;
  full pytest re-run is the user's gating step.

### Changes Intentionally Skipped

- **No edits to `TODO.md`.** The audit agent's continuation guidance
  (paused-agent WIP, Dependabot triage, Wave 1) is still the right
  next-action list. This recovery is small enough that adding a TODO
  entry would be low-value spam.
- **No edits to `RUNNING.md`.** The themed-`/docs` row at line 116
  already describes the now-correct state.
- **No touch on `stash@{0}`, `backup/chore-gov-pre-slim`, or any
  untracked frontend file.** Those belong to the paused styleguide
  agent's WIP; per the audit agent's handoff, they are held for
  human/owner decision.
- **No `redoc` theming.** Out of scope for this recovery; ReDoc remains
  default light theme until a follow-up ticket addresses it.
- **No git commit.** Per project rules, commits require explicit user
  request.

### Remaining Handoff

- Run the four verification commands above once WMI is healthy.
- If any test fails, the most likely culprit is the `swagger-ui-dist`
  CDN URL in Swagger UI 5.x changing across FastAPI versions; the
  `test_swagger_docs_serves_themed_html` assertion would catch it
  cleanly and the fix is to update the asserted substring.
- The paused-styleguide-agent decision (resume vs cherry-pick `07d05ab`)
  remains the higher-priority blocker for FEATURE-0034 proper; this
  recovery only landed the API-docs chrome slice.

---

## 2026-04-26 — Project state / cleanup / handoff audit

- **Agent**: Human + Developer (audit / steward)
- **Goal**: Audit repo, git/GitHub, specs, and TODOs after a busy day of
  parallel agent work; produce a clean handoff anchored on `TODO.md`.

### Reviewed

- `README.md`, `PROJECT_CONTEXT.md`, `TODO.md`, `SESSION_LOG.md` (this file),
  `DECISIONS.md`, `AGENTS.md`.
- `.cursor/README.md`, `.cursor/state/README.md`,
  `.cursor/state/decisions-pending.md` (gitignored, hook-only noise).
- `specs/trading-lab-platform/` — `requirements.md`, `design.md`,
  `tasks.md`, the 12-epic `tasks/` tree.
- Live `gh` state: open PRs, Dependabot alerts, recent CI runs on `main`.

### Git State (snapshot)

- Branch: `main`, in sync with `origin/main` at
  `8174b0b ci(docker): build trading-base before service images and publish to GHCR (#17)`.
- Working tree: 18 untracked frontend files (paused-agent WIP for
  FEATURE-0034 `/styleguide`).
- Stashes: `stash@{0}: On github-public-governance: wip-all-before-slim-pr3`
  — content is fully captured on `backup/chore-gov-pre-slim`; redundant.
- Local branches: `main`, `backup/chore-gov-pre-slim` (2 commits ahead of
  `main`: `9913a86` frontend-init compose service, `07d05ab` styleguide
  WIP), and three throwaway PR refs `pr-13`, `pr-15`, `pr-16` from earlier
  Dependabot triage.

### GitHub State (snapshot)

- 12 open Dependabot PRs (#4-14, #16); all `BLOCKED` on solo-owner
  CODEOWNERS review. Reviews posted on the three load-bearing ones (#9
  postcss, #13 next 16, #16 vitest 4). PR #15 closed as exact duplicate of
  #16.
- 3 Dependabot alerts open: `postcss` #7 (transitive via `next`), `vite`
  #8, `esbuild` #9 (both via `vitest`). Resolution paths documented in PR
  reviews.
- Required-check rollup on `main`: green for all six required contexts
  (`Analyze`, `lint · ruff`, `types · mypy --strict`,
  `test · unit + strategy + cursor harness`, `test · security suite`,
  `security · gitleaks`). `docker · build images` is now green on `main`
  after PR #17 (was the only post-PR #3 regression).

### Changes Made

- `TODO.md` — refreshed 2026-04-26 status block (PR #3 + #17 marked done
  with merge commits cited), added an explicit
  **Agent Coordination / Conflict Status** section with handoff
  instructions for future agents.
- `SESSION_LOG.md` — this entry.
- `specs/trading-lab-platform/tasks.md` — added
  **Addendum: Agent Coordination and Handoff (2026-04-26)** plus a
  **PR #17 (docker · build images regression)** audit row appended to the
  existing 2026-04-26 status table.
- Local repo housekeeping (no on-disk content changes): drop the
  throwaway Dependabot triage refs `pr-13`, `pr-15`, `pr-16` (these are
  just `git fetch` mirrors of PRs that still exist on the remote;
  reversible with `git fetch origin pull/N/head:pr-N`). The
  `wip-all-before-slim-pr3` stash and `backup/chore-gov-pre-slim` branch
  are **kept** — they hold the paused agent's work-in-progress and
  dropping them risks silent data loss.

### Changes Considered but Skipped

- **Untracked styleguide files in working tree** — paused-agent WIP. Not
  this session's to land; explicitly held per user instruction.
- **Delete `backup/chore-gov-pre-slim`** — local-only branch is the sole
  holder of `9913a86` (frontend-init compose svc) and `07d05ab` (styleguide
  WIP). Held per user instruction until the WIP decision lands.
- **`.cursor/state/decisions-pending.md`** — gitignored
  (`.gitignore:75`), hook-only noise; not committed, no action needed.
- **Rules / hooks / skills under `.cursor/`** — no observed reliability
  problem from this session; the harness behaved as documented. No high-
  value edit.
- **`PROJECT_CONTEXT.md`, `DECISIONS.md`, `AGENTS.md`** — clean and
  current; no changes earned their place.
- **Reorganizing `TODO.md` Sprint 1 milestones** — these still represent
  the foundation slice. The `tasks.md` Wave 1 list in
  `specs/trading-lab-platform/` is the canonical roadmap; `TODO.md` keeps
  pointing at it. No reorganization needed.

### Agent Coordination Status

Documented in `TODO.md` under **Agent Coordination / Conflict Status**.
Short version: two parallel sessions ran 2026-04-26; this session owned
the governance + CI fixes (PR #3, #17) and never touched the styleguide;
the paused agent owned FEATURE-0034 (styleguide) and its WIP is captured
on `backup/chore-gov-pre-slim` and as untracked files in the working tree.
No file-level conflicts exist between the two scopes. Handoff path is
documented in `TODO.md`.

### Spec Addendums

- `specs/trading-lab-platform/tasks.md` — appended:
  - One row in the existing 2026-04-26 audit table flagging PR #17 as the
    `docker · build images` regression fix and citing the `docker` driver
    trade-off.
  - **Addendum: Agent Coordination and Handoff (2026-04-26)** describing
    the parallel-session pattern, where to find paused WIP, and how future
    agents should pick continuation work.

No requirement-level addendum (no architecture, risk, or LLM-isolation
behavior changed during this session).

### Remaining Risks

- **Paused-agent WIP retention** — if `backup/chore-gov-pre-slim` is
  deleted before the styleguide is cherry-picked into a PR, `9913a86` and
  `07d05ab` are lost (local-only).
- **Dependabot lockfile-regen recurrence** — PRs #13, #14, #16 all share
  the `npm error Missing: @esbuild/* from lock file` failure mode. Either
  patch CI's `npm ci` step or do a one-shot manual lockfile regen per
  Dependabot PR. Tracked in PR #16 review.
- **`docker · build images` cold cache** — `docker` driver does not
  support GHA cache, so each PR rebuilds `trading-base` (~3-5 min).
  Acceptable for now; warm registry cache via `trading-base.yml` is the
  recorded follow-up.

### Next Agent Handoff

Read `TODO.md` first. The next concrete pieces of work, in priority order:

1. **Decide on the paused-agent WIP** (blocker for `/styleguide`). Resume
   that agent or cherry-pick `07d05ab` into `feat(frontend): styleguide
   inventory`.
2. **Land the postcss `overrides`** (clears Dependabot alert #7). One-line
   `package.json` edit + lockfile bump.
3. **Pick one Dependabot lockfile-regen path** (PR #16 or a CI patch) so
   the `npm ci` failures stop blocking the rest of the queue.
4. **Tackle Wave 1 of `specs/trading-lab-platform/tasks.md`** when the
   above three are unblocked: FEATURE-0001, 0002, 0021, 0022, 0037, 0039,
   0040.

---

## 2026-04-26 — PR #17 docker · build images regression fix

- **Agent**: Developer
- **Goal**: Land the `trading-base` build step that was sliced out of
  PR #3, so the `docker · build images` job stops failing on every PR.
- **Done**:
  - Cherry-picked `44143ee` onto `fix/ci-trading-base-build` and iterated
    five times to land cleanly: `068a5da` (bogus `ignore-error=true`),
    `c4fa331` (GHCR auth so cache miss is 404 instead of 403), `ddfcd39`
    (drop registry `cache-from` entirely; use GHA scope only), `6af6fc0`
    (try `build-contexts: docker-image://...` — still resolved via
    registry), `fd8a6d8` (switch buildx to `driver: docker` so host
    Docker shares the image store), `c4241bf` (add
    `frontend/public/.gitkeep` for a pre-existing Dockerfile copy bug
    surfaced once frontend got far enough to actually build).
  - Final shape: `docker` driver, no GHA cache for the docker job,
    `trading-base.yml` workflow publishes `:cache` to GHCR for external
    consumers, frontend has a permanent `public/` placeholder.
- **Verified**:
  - `gh run view 24963450616 --json jobs` → `docker · build images`
    completed `success` in 4m9s (trading-base 2m30s, engine/backend ~12s
    each, frontend ~1m).
  - All six required-check contexts green on the merge candidate.
  - PR #17 merged via `gh pr merge 17 --admin --squash --delete-branch`
    at `8174b0b` (2026-04-26T18:15Z).
- **Blocked / next**:
  - `docker` driver does not support `cache-from: type=gha`. Cold pip
    install per PR run is acceptable for now; warm registry cache via
    `trading-base.yml` is a follow-up once that workflow has run on
    `main` at least once.

---

## 2026-04-26 — PR #3 admin merge + Dependabot triage

- **Agent**: Developer
- **Goal**: Land `chore(github): public-repo governance, CI hardening,
  and spec addenda` and triage the Dependabot PRs Dependabot opened
  immediately after.
- **Done**:
  - Sliced `chore/github-public-governance` from a 5-commit chore branch
    (the other 3 commits — frontend-init compose service, docker base
    workflow, full styleguide inventory — held back to keep PR #3
    minimal). Pushed three additional commits onto the slim branch to
    fix Next 15 dynamic-route `params` typing
    (`fix(frontend): await Promise params on Next 15 dynamic routes`,
    `fix(frontend): await Promise searchParams on runs compare page`,
    plus the originally-scoped `fix(ci+deps): clear ruff/mypy regressions
    and resolve 7 Dependabot alerts`).
  - PR #3 merged at `a96280f` via `--admin --squash`.
  - Dependabot opened 14 PRs against `main` immediately after; this
    session reviewed and held: closed PR #15 as exact duplicate of #16,
    posted substantive `--comment` reviews on PR #9 (postcss), #13
    (next 16 — flagged as needing a coupled React 19 + eslint-config-next
    bump and a manual lockfile regen; recommended close-and-replace),
    and #16 (vitest 2→4 — flagged the `npm ci` lockfile-regen failure
    pattern that affects PRs #13 / #14 / #16).
- **Verified**:
  - PR #3 merge: `gh pr view 3 --json state,mergedAt,mergeCommit` →
    `MERGED` at `a96280f`, 2026-04-26T14:40:53Z.
  - Six required checks green at merge time; `docker · build images` was
    the only failing job and is non-required (separately fixed in PR
    #17).
  - Dependabot alert #7 (postcss) explicitly investigated:
    `vulnerable_range: <8.5.10`, `first_patched: 8.5.10`. The advisory
    keys on the `postcss@8.4.31` that `next@15.5.15` bundles internally,
    not on the direct devDep at `^8.5.10`. PR #9 alone (8.5.10 → 8.5.12)
    will not flip the alert; recommended pairing with a `package.json`
    `overrides.postcss` block in the PR review.
- **Blocked / next**:
  - 12 open Dependabot PRs still BLOCKED on solo-owner CODEOWNERS
    review. Use `--admin` admin-merge per PR after lockfile-regen and
    review.

## 2026-04-26 — PR #3 Next 15 dynamic route params (CI build)

- **Agent**: Developer
- **Goal**: Fix failing `npm run build` on PR #3 after Next 15 upgrade (`params`
  must be `Promise` on dynamic app routes).
- **Done**:
  - `frontend/app/backtests/[runId]/page.tsx` and
    `frontend/app/runs/[runId]/page.tsx`: `params: Promise<{ runId: string }>` +
    `await params`.
  - `frontend/next.config.mjs`: drop deprecated `experimental.typedRoutes`
    (typed routes remain off by default on Next 15).
  - Follow-up: `frontend/app/runs/compare/page.tsx` — `searchParams` as
    `Promise` + `await` (Next 15 `PageProps`).
- **Verified**: Local `npm run build` not re-run after ENOSPC on `npm install`;
  change matches Next 15 App Router contract; only PR-scoped files staged.
- **Blocked / next**: Confirm GitHub Actions frontend job green after compare
  page fix; then admin-merge PR #3.

## 2026-04-26 — PR #3 CI unblock + Dependabot (next 15 / postcss)

- **Agent**: Developer
- **Goal**: Land fixes for failing `ruff` / `mypy` on PR #3 and bump frontend deps
  to clear seven Dependabot alerts (`next`, `postcss`, transitive `glob`).
- **Done**:
  - Commit `9ca328f` on `chore/github-public-governance`: Generator fixture typing
    and ruff-format six files; `frontend/package.json` + lockfile for next
    `15.5.15`, eslint-config-next `15.5.15`, postcss `^8.5.10`.
- **Verified** (with unrelated work stashed): `ruff check .`, `ruff format --check .`,
  `mypy --strict --explicit-package-bases .` all green; `pytest
  tests/security/test_no_secrets.py` passed. Full `npm install` failed locally
  with ENOSPC; lockfile updated with `npm install --package-lock-only`; CI
  frontend job is the install gate.
- **Blocked / next**: Wait for GitHub Actions on PR #3; admin-merge if solo owner.

## 2026-04-26 — GitHub maintainer settings via `gh` API

- **Agent**: Developer
- **Goal**: Apply repo security and `main` branch protection per
  `gh_cli_maintainer_settings` plan (MCP cannot toggle these).
- **Done**:
  - `PATCH repos/finalFlick/market-prediction` — secret scanning + push
    protection **enabled**.
  - `PUT .../vulnerability-alerts` — **204** (Dependabot alerts on).
  - `PUT .../automated-security-fixes` — **200** `enabled: true` (security
    update PRs on); `security_and_analysis.dependabot_security_updates` now
    **enabled**.
  - `PUT .../branches/main/protection` — required checks (with `\u00b7` in JSON
    to avoid PowerShell corrupting middots), `require_code_owner_reviews: true`,
    1 approval, strict status checks, no force-push, conversation resolution on.
- **Verified**:
  - `gh api repos/finalFlick/market-prediction --jq '.security_and_analysis'`
    → secret_scanning + push_protection enabled; dependabot_security_updates
    enabled.
  - `gh api -i .../vulnerability-alerts` → **204 No Content**.
  - `gh api -i .../automated-security-fixes` → **200** body `enabled: true`.
  - `gh api .../branches/main/protection --jq ...` → contexts include
    `lint · ruff`, …, `Analyze`; `code_owner_review: true`.
- **Blocked / next**:
  - `gh auth refresh -s repo,security_events,workflow` was started for optional
    scope; **`repo` alone sufficed** — cancel device flow if still pending.
  - Merge workflow files to `main` so every required check name exists on
    default branch; first green `main` run validates protection.

## 2026-04-26 — Public GitHub guidance and CI hardening

- **Agent**: Developer
- **Goal**: Record public-repo threat model in steering docs; add maintainer
  contributor guide; Dependabot, CodeQL, CODEOWNERS, composite Python CI setup;
  append `specs/trading-lab-platform` addenda (Requirement E + design/tasks).
- **Done**:
  - Steering: [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md),
    [`.cursor/README.md`](.cursor/README.md),
    [`.cursor/rules/security.mdc`](.cursor/rules/security.mdc),
    [`WORKFLOW.md`](WORKFLOW.md), [`README.md`](README.md),
    [`RUNNING.md`](RUNNING.md) (maintainers pointer).
  - [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md) (fork PR + maintainer checklist).
  - GitHub: [`.github/dependabot.yml`](.github/dependabot.yml),
    [`.github/workflows/codeql.yml`](.github/workflows/codeql.yml),
    [`.github/CODEOWNERS`](.github/CODEOWNERS),
    [`.github/actions/setup-trading-lab-python/action.yml`](.github/actions/setup-trading-lab-python/action.yml),
    updated [`.github/workflows/ci.yml`](.github/workflows/ci.yml),
    comment on [`.github/workflows/pages.yml`](.github/workflows/pages.yml).
  - Spec addenda: [`requirements.md`](specs/trading-lab-platform/requirements.md),
    [`design.md`](specs/trading-lab-platform/design.md),
    [`tasks.md`](specs/trading-lab-platform/tasks.md); audit note on
    [FEATURE-0039](specs/trading-lab-platform/tasks/deployment-security-ci/cicd_quality_gates_0039.md).
- **Verified**:
  - `py -3.12 -m pytest tests/cursor_harness -q` → 131 passed
  - `py -3.12 -m ruff check .` → all checks passed
  - `py -3.12 -m pytest -q -m "not slow and not integration and not e2e"` →
    collection `MemoryError` on this host (environment); not attributed to this
    doc/CI-only change set
  - `py -3.12 -m ruff format --check .` / `mypy --strict` → pre-existing issues in
    other paths (unchanged by this session)
- **Blocked / next**: Enable GitHub Rulesets, secret scanning, and Dependabot
  alerts in repo Settings if not already on; confirm `@finalFlick` in CODEOWNERS.

## 2026-04-26 — Swagger `/docs` themed to operator styleguide

- **Agent**: Developer
- **Goal**: Align FastAPI OpenAPI Swagger UI with FEATURE-0034 / Tailwind
  operator-console palette (dark, token-matched) without new dependencies.
- **Done**:
  - Added [`backend/api/static/swagger-trading-lab.css`](backend/api/static/swagger-trading-lab.css)
    with `.swagger-ui` overrides synced to `frontend/tailwind.config.ts`.
  - Updated [`backend/api/app.py`](backend/api/app.py): `docs_url=None`,
    `StaticFiles` on `/static`, custom `GET /docs` via `get_swagger_ui_html`
    and `syntaxHighlight.theme: obsidian`.
  - Extended [`tests/e2e/test_api_app.py`](tests/e2e/test_api_app.py) with
    Swagger HTML and CSS smoke tests.
  - Documented `/docs` in [`RUNNING.md`](RUNNING.md); addenda in
    [`specs/trading-lab-platform/tasks.md`](specs/trading-lab-platform/tasks.md)
    and [`FEATURE-0034`](specs/trading-lab-platform/tasks/frontend-operator-experience/style_guide_component_library_0034.md).
- **Verified**:
  - `py -3.12 -m pytest tests/e2e/test_api_app.py -q` → 9 passed
  - `py -3.12 -m ruff check backend/api/app.py tests/e2e/test_api_app.py` →
    all checks passed
  - `py -3.12 -m mypy --strict backend/api/app.py tests/e2e/test_api_app.py` →
    success
  - `py -3.12 -m pytest -q` → `294 passed, 3 warnings in 234.42s`
- **Blocked / next**: Theme `/redoc` in a follow-up if operators want parity.

## 2026-04-26 — dev-speed docker, MVP-0 run UI audit, and Cursor workflow hardening

- **Agent**: Developer
- **Goal**: Finalize the session's MVP-0 run/API/UI and Docker development
  changes, audit them into `specs/trading-lab-platform`, strengthen the weak
  frontend styleguide, improve `.cursor` guidance based on observed workflow
  failures, and commit the completed work.
- **Done**:
  - Added shared Docker base workflow: `Dockerfile.base`,
    `Dockerfile.research`, dev compose override, `dev.py`, and docs for the
    fast Docker development loop.
  - Refactored backend and trading-engine Dockerfiles to inherit from
    `trading-base`.
  - Added Windows Docker Desktop bind-mount masks for `.venv`, `.git`, caches,
    and frontend generated folders after measuring them as the cause of the
    15+ minute pytest run.
  - Audited current work in
    `specs/trading-lab-platform/tasks.md` and added notes to FEATURE-0003 and
    FEATURE-0038.
  - Rewrote FEATURE-0034 as a build-ready cyberpunk hacker styleguide and
    component-library spec with tokens, layout patterns, component categories,
    demo data expectations, and validation gates.
  - Made `dev.py` stdlib-only after validation showed bare Windows Python did
    not have `click`, preserving the same CLI commands without host setup.
  - Switched frontend Docker installs to the committed lockfile (`npm ci`) and
    made the dev frontend command populate the `trading-node-modules` volume on
    first start.
  - Made dev dependency volume names explicit so `dev.py reset-deps` removes
    the same volumes Compose mounts.
  - Added dev-only `types-PyYAML==6.0.12.20260408` after checking PyPI current
    metadata (released 2026-04-08, Python >=3.10, tested with mypy 1.20) so
    the container mypy gate is reproducible.
  - Added `.cursor/rules/component-first.mdc`, strengthened frontend/docker
    rules, corrected hook-router semantics in `.cursor/hooks/README.md`, and
    expanded `.cursor/context-router.json` routing for styleguide and Windows
    Docker prompts.
  - Updated `README.md`, `RUNNING.md`, `docs/UI_REQUIREMENTS.md`, and `TODO.md`
    so future agents can resume from the current state.
- **Verified**:
  - `docker build -f Dockerfile.base -t trading-base .` → success; subsequent
    cached rebuild took ~2.8 s.
  - `docker compose -f docker-compose.yml -f docker-compose.dev.yml build` →
    success after `trading-base` existed.
  - `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d` →
    backend, frontend, research, engine, redis, and duckdb started.
  - Backend health check via PowerShell `Invoke-WebRequest` →
    `200 {"status":"ok", ...}`.
  - Backend hot reload verified from logs:
    `WatchFiles detected changes in 'backend/api/routers/runs.py'. Reloading...`.
  - Windows bind-mount investigation: `/app` visible tree dropped from ~3 GB to
    5.7 MB; `du /app` dropped from 104 s to 1.4 s.
  - Dev-container unit suite:
    `pytest -q -m "not slow and not integration"` →
    `291 passed, 1 deselected, 3 warnings in 53.24s`.
  - Dev-container full suite: `pytest -q` →
    `292 passed, 3 warnings in 52.89s`.
  - Security suite: `pytest tests/security -q` → `25 passed`.
  - Research container import smoke:
    `torch=2.11.0+cu130`, `lightgbm=4.6.0`, `vectorbt=1.0.0`,
    `xgboost=3.2.0`.
  - `docker compose ... down` then `up -d` with preserved volumes → 24.7 s.
  - `ruff check dev.py` → all checks passed.
  - `mypy --strict --explicit-package-bases dev.py` → success.
  - `python dev.py --help` on host Windows Python → displays command help
    without requiring `click`.
  - `docker compose ... exec frontend npm run typecheck` → success.
  - `docker compose ... exec -e NODE_ENV=production frontend npm run build` →
    success; 19 app routes generated/validated.
  - `docker compose -f docker-compose.yml -f docker-compose.dev.yml build frontend`
    → success; production image builds with `npm ci` and Next standalone output.
  - `mypy --strict --explicit-package-bases data research strategies risk
    backtests execution monitoring backend runs learning dev.py` → success
    after installing the pinned PyYAML stubs.
- **Blocked / next**:
  - Production compose now expects a locally tagged `trading-base`; CI should
    build/tag it explicitly or move to a compose target/registry-cache pattern.
  - `/styleguide` itself is not implemented yet; FEATURE-0034 is now strong
    enough to drive that implementation.
  - Full global `ruff check .`, `mypy --strict .`, frontend lint/typecheck/build,
    e2e, and backtest smoke still need to be run or remediated before a release
    PR is considered complete.

---

## 2026-04-25 — no-key MVP slice (ingest, optional Redis, spec addendum)

- **Agent**: Developer
- **Goal**: Public REST ingesters without exchange keys, optional Redis with in-memory event bus, operator env docs, spec addendum; ship 0.3.1.
- **Done**:
  - `data/ingest/binance_public.py`, `coinbase_public.py`, `yfinance_source.py`; `data/ingest/run.py` `--source`; `Exchange.YAHOO`; `yfinance` in `dev` + `public-data` extra.
  - `backend/api/routers/system.py` `redis_disabled`; `runs/events/*`; frontend health badges; e2e `test_health_redis_optional`.
  - `tests/data/`, `tests/runs/test_in_memory_bus.py`; `tests/security/test_no_secrets.py` git-tracked `.env` only.
  - `docs/REMINDERS.md`, `.env.example`, `RUNNING.md`; `specs/trading-lab-platform` requirements/design/tasks addendum + FEATURE-0041–0043.
  - `CHANGELOG` 0.3.1, `pyproject` 0.3.1.
- **Verified**:
  - `py -3.12 -m pytest -q` → 265 passed
  - `py -3.12 -m pytest -q -m e2e` → 10 passed
  - `ruff check .` → pass; `mypy --strict --explicit-package-bases .` → 168 files
  - `py -3.12 -m backtests.smoke` → smoke OK; `py -3.12 -m monitoring.audit verify --tables critical` → all_ok
- **Blocked / next**: n/a

## 2026-04-25 — mvp-0 build slice (full stack)

- **Agent**: Developer
- **Goal**: Complete MVP-0 build slice: quality gates, invariants, runs/learning/audit/backend/frontend, acceptance e2e, docs, DEC-007/008/009, v0.3.0.
- **Done**:
  - **Schema fix:** Renamed `state_transitions` column `at` → `transitioned_at` (DuckDB reserved/parse conflict).
  - `monitoring.canonical_json`, backtest det smoke anchor, `pytest -m det`, hash-chain `ha_*` + `monitoring.audit verify`.
  - `RiskAudit` / `RiskDecision`, `data/repositories/audit/duckdb_risk_audit.py`, security scans (path-only risk, no bypass in app roots, `runs/` LLM isolation).
  - `runs/` (RunConfig, orchestrator, recovery, outbox), `execution` reconcile stub, `learning/` OOS scorers, `data/seeds` + `adjust` helpers.
  - API: runs list, health+audit+metrics, kill-switch; frontend kitsune + MVP-0 pages.
  - `docs/MVP0_READINESS.md`, `CHANGELOG` 0.3.0, `DECISIONS` DEC-007/008/009, `pyproject` 0.3.0.
- **Verified**:
  - `ruff check .` → all checks passed
  - `mypy --strict --explicit-package-bases .` → Success (155 source files)
  - `py -3.12 -m pytest -q` → 256 passed
  - `py -3.12 -m backtests.smoke` → smoke OK
  - `py -3.12 -m monitoring.audit verify --tables critical` → all_ok: true
- **Blocked / next**: n/a

## 2026-04-25 — merge docsite worktree into main

- **Agent**: Developer
- **Goal**: Re-integrate the `experiment/specs-gh-pages` worktree
  (`market-prediction-pages`) into `main` and remove the split.
- **Done**:
  - Merged `experiment/specs-gh-pages` (`mkdocs.yml`, `docsite/`,
    `.github/workflows/pages.yml`).
  - Added `docsite/` to `ruff` and `mypy` excludes in `pyproject.toml`.
  - Removed sibling worktree and the local + remote
    `experiment/specs-gh-pages` branch.
- **Verified**: `ruff check .`, `mypy --strict --explicit-package-bases .`,
  `pytest -q`, `pytest -q -m e2e`.
- **Blocked / next**: Pages workflow now publishes from `main`.

## 2026-04-25 — docsite README for GitHub Pages

- **Agent**: Developer
- **Goal**: Add a maintainer-facing `docsite/README.md` for the Pages/MkDocs
  pipeline (distinct from repo root `README.md`) and link it from `index.md`.
- **Done**: `docsite/README.md`; `docsite/index.md` maintainer link.
- **Verified**: `mkdocs build` in worktree (success).
- **Blocked / next**: none.

## 2026-04-25 — trading-lab spec site (MkDocs + GitHub Pages, worktree)

- **Agent**: Developer
- **Goal**: Add a themed MkDocs + GitHub Pages deploy for
  `specs/trading-lab-platform/` and project docs, entirely on
  `experiment/specs-gh-pages` in a sibling git worktree so `main` stays
  untouched by other agent work.
- **Done**:
  - Sibling worktree: `../market-prediction-pages` on
    `experiment/specs-gh-pages`.
  - `mkdocs.yml` + `docsite/` (index, kitsune-cyberpunk `extra.css`, sync
    hook, mermaid `fence_div_format` + `javascripts/mermaid-init.js`, pinned
    `docsite/requirements.txt` — not in `pyproject.toml`).
  - `.github/workflows/pages.yml` (path-filtered push, `concurrency: pages`,
    `actions/deploy-pages@v4` + `upload-pages-artifact@v3`).
- **Verified**:
  - `py -3.12 -m pip install -r docsite/requirements.txt` in worktree
  - `py -3.12 -m mkdocs build` in worktree (success; link warnings to
    out-of-doc paths like `.cursor/` expected)
  - Built HTML contains `<div class="mermaid">` in
    `specs/trading-lab-platform/design/`
  - `git push` → branch `experiment/specs-gh-pages` on `origin`
  - `gh api ... deployment-branch-policies` → allowed
    `experiment/specs-gh-pages` on environment `github-pages` (unblocks
    `actions/deploy-pages@v4` with that environment)
  - GitHub Actions run `pages` (run id `24939587230`) → success (build + deploy)
  - `gh api .../pages` → `https://finalflick.github.io/market-prediction/`
  - Live home page fetches and shows themed “Trading Lab — spec library”
- **Blocked / next**:
  - Rebase the worktree on `origin/main` when you want the latest spec content
    (`git fetch origin && git rebase origin/main` in
    `../market-prediction-pages`).
  - If you merge this into `main`, add `docsite/` to ruff/mypy excludes
    in `pyproject.toml` (per plan).

## 2026-04-25 — mvp-0 live broker registration lock slice

- **Agent**: Developer
- **Goal**: Implement the MVP-0 live broker registration lock contract from
  `specs/trading-lab-platform` with TDD and runner integration.
- **Done**:
  - Added `execution/brokers/registry.py` with
    `LiveBrokerRegistry` and `LiveAdapterRegistrationForbidden`.
  - Added `configs/runtime.yaml` with default
    `live_adapters_unlocked: false`.
  - Added `BinanceLive` / `CoinbaseLive` aliases for design parity.
  - Updated `execution/runner.py` to register paper by default and reject
    locked live brokers with a clear Click error.
  - Added `tests/security/test_live_registration_forbidden.py` (5 tests).
  - Added resolution notes to FEATURE-0021 and FEATURE-0022 task files.
  - Added `DEC-006` and created `CHANGELOG.md`; bumped version to `0.2.0`.
- **Verified**:
  - `py -3.12 -m pytest -q tests/security/test_live_registration_forbidden.py`
    → 5 passed
  - `py -3.12 -m pytest -q tests/security/` → 21 passed
  - `py -3.12 -m pytest -q -m "not slow and not integration"` → 204 passed
  - `ruff check execution/brokers/registry.py execution/runner.py tests/security/test_live_registration_forbidden.py` → all checks passed
  - `py -3.12 -m mypy --strict execution/brokers/registry.py execution/runner.py tests/security/test_live_registration_forbidden.py` → success
  - `py -3.12 -c "import execution.brokers.binance, execution.brokers.coinbase; print('ok')"` → ok
  - `ruff check .` → fails on pre-existing unrelated issues in
    `.cursor/hooks/check_dependency_research.py`, `backtests/engine.py`,
    and `monitoring/logger.py`.
- **Blocked / next**:
  - Continue Wave 1 with FEATURE-0039 (CI/CD quality gates) so global lint and
    typecheck regressions are enforced systematically.

---

## 2026-04-25 — trading-lab-platform task system

- **Agent**: Planner / Spec
- **Goal**: Convert the approved `trading-lab-platform` requirements and
  design into an epic and feature ticket system that explains why/what,
  not implementation how.
- **Done**:
  - Replaced the placeholder `specs/trading-lab-platform/tasks.md` with an
    execution index, roadmap, assumptions, traceability matrix, open
    questions, and quality checklist.
  - Added `specs/trading-lab-platform/tasks/` with 12 epic folders and 40
    feature tickets covering MVP-0, v1, and later gated work.
  - Recorded the `.kiro` path mismatch as an assumption: this repo's active
    spec tree is `specs/trading-lab-platform/`.
  - Updated `TODO.md` to point implementation agents at the new task system.
- **Verified**:
  - `Glob specs/trading-lab-platform/tasks/**/*.md` → 52 Markdown files
    found (12 epics + 40 feature tickets).
  - Generated link check over `specs/trading-lab-platform/tasks.md` →
    `indexed_paths=52 unique_paths=52 missing=0`.
  - `ReadLints` on `specs/trading-lab-platform/tasks.md` and
    `specs/trading-lab-platform/tasks/` → 0 linter errors.
- **Blocked / next**:
  - Full code validation (`pytest -q`, `ruff check .`, `mypy --strict .`)
    was not run because this session only changed planning Markdown.
  - Next implementation agents should start with Wave 1 in
    `specs/trading-lab-platform/tasks.md`.

---

## 2026-04-25 — trading-lab-platform spec finalization + de-risking POCs

- **Agent**: Human + Architect (planner) + scripted POC runner
- **Goal**: Finish the `trading-lab-platform` spec session through Phase 2
  (design) at production quality, then run a quick set of throwaway POCs
  to expose any gap before tasks.md.
- **Done**:
  - `specs/trading-lab-platform/requirements.md` — added top-level
    `Phasing` section and inline `[MVP-0] / [v1] / [v1.x] / [v1.1] /
    [v1.2-4] / [v2.x] / [FUTURE]` tags across Reqs 4, 5, 11, 16, 18,
    21, 22, 26, 33, 41, 44 so nothing was deleted while v1+ scope
    moved off the MVP-0 slab.
  - `specs/trading-lab-platform/design.md` — new `MVP-0 Scope and
    Sequencing` section (Day-0 Invariants, Deliverables, Acceptance,
    12-step v1 plan); Canonical-JSON serialization spec in §9; staggered
    hash-chain (critical tables only at MVP-0) in §15; `LiveBrokerRegistry`
    + `LiveAdapterRegistrationForbidden` for Coinbase/Binance until
    v1.1; LLM calibration split by `task_type`; Schwab CSV-first +
    OAuth `[v1.x]`; long-horizon single-stock equities flagged
    `degraded` + capped at R-1 until v1.4.
  - 11 throwaway POC scripts under `pocs/` (deterministic backtest,
    risk-bypass toy + real-engine, artifact replay, event stream +
    DuckDB/SQLite outbox, paper broker fees/slippage/partial,
    LLM isolation, config snapshot, learning-loop scoreboard,
    quants-first signal experiments, latency + 1M-row pipeline)
    plus `pocs/run_all_pocs.py`. `poc_results.md` summarises the run.
  - `pyproject.toml` — added `pocs` to `[tool.ruff] extend-exclude`
    so throwaway code never gates the strict ruleset.
  - Targeted spec deltas motivated by POC 8 (learning loop):
    - `requirements.md` Req 44.9 (new): every lever scorer consumes
      OOS / purged-embargo outcomes only; raw IS PnL forbidden;
      `tests/learning/test_no_in_sample_scoring.py` enforces.
    - `design.md` Component 15: matching implementation note tying
      `Scorer.update()` to `RunSummary.oos_metrics` with a typed
      Pydantic boundary, citing the POC.
- **Verified**:
  - `ReadLints` on `requirements.md`, `design.md`, `pyproject.toml`
    → 0 errors after every change.
  - `python pocs/run_all_pocs.py` → 11/11 `OK` (POC 2b cleanly
    `SKIP`s when project deps aren't in the active interpreter).
  - `ruff check .` → only 2 pre-existing warnings in
    `backtests/engine.py` and `monitoring/logger.py`; `pocs/` no
    longer surfaces in default sweeps.
  - File-size sanity: `requirements.md` 1371 → 1465 lines (+94,
    additive); `design.md` 4026 → 4639 lines (+613, additive);
    no requirement or design section removed.
- **Blocked / next**:
  - Phase 3 (`tasks.md`) for `trading-lab-platform` is still pending;
    user has not yet approved the design for that step.
  - Real `RiskEngine` POC (`pocs/risk_engine_bypass/run_poc_real.py`)
    needs a 3.11 venv with `pip install -e .` to run end-to-end;
    optional CI job once that venv exists.
  - Test stubs `tests/security/test_live_registration_forbidden.py`
    and `tests/learning/test_no_in_sample_scoring.py` are referenced
    by Reqs 4.6 and 44.9 but not yet implemented; they belong in
    `tasks.md`.

---

## 2026-04-25 — prompt-context-router (spec session)

- **Agent**: Human + planner / developer / tester subagents
- **Goal**: Auto-inject relevant `.cursor` steering-file excerpts into the
  agent's context, both at session start and dynamically during a chat,
  via Cursor hooks.
- **Done**:
  - Spec session under `specs/prompt-context-router/` with
    `requirements.md`, `design.md`, `tasks.md`.
  - Two new hook scripts:
    - `.cursor/hooks/prompt_capture.py` (`beforeSubmitPrompt`) — persists
      the user prompt (redacted, capped at 8 KB) to
      `.cursor/state/last-prompt.json`.
    - `.cursor/hooks/prompt_context_router.py` (`postToolUse`) — reads
      the captured prompt + tool call, evaluates a routing table, and
      emits `additional_context` snippets.
  - Pure routing core split into `_router_types.py`, `_router_io.py`,
    `_router_core.py` (load/validate, match, excerpt, prune, route) —
    stdlib only, fail-open everywhere.
  - Routing table at `.cursor/context-router.json` (v1, 9 rules:
    risk-policy, evaluation-gates, signal-research, data-ingest,
    frontend-dashboard, infra-deployment, llm-isolation, spec-workflow,
    workflow-discipline).
  - `session_init.py` augmented with a "Steering files (read on demand)"
    doc map and a "How to invoke" pointer to the `session-init` skill;
    bumped `MAX_CONTEXT_CHARS` 6000 → 8000.
  - Wired both hooks into `.cursor/hooks.json` (5 s timeout, fail-open).
  - Operator doc at `.cursor/hooks/README.md`; linked from
    `PROJECT_CONTEXT.md`.
  - Runtime state files added to `.gitignore`.
  - Spec-driven semantic refinement: trigger keys in routing rules are
    OR-combined (was AND-between-keys). `tool_name_in` remains an
    AND filter. Spec docs and tests updated to match.
  - 16 new test files under `tests/cursor_harness/` covering
    routing-table sanity, load/validate, match, excerpt, prune, route,
    determinism, hook-contract subprocess tests, hooks.json schema,
    session-init doc map, and an end-to-end smoke test.
- **Verified**:
  - `ruff check .cursor/hooks tests/cursor_harness` → All checks passed
  - `python -m pytest tests/cursor_harness/ -q` → 100 passed in 2.85s
  - Live smoke: `prompt_capture` + `prompt_context_router` end-to-end
    against the real project: prompt-only trigger injects
    `docs/RISK_POLICY.md` + `.cursor/rules/risk-management.mdc`;
    tool-only trigger (`Read backtests/run.py`) injects
    `docs/EVALUATION.md`; unrelated paths emit `{}` cleanly;
    session-memory dedup confirmed by repeating the same call.
  - `mypy --strict` not run: not installed in the local Python 3.9
    interpreter (project requires 3.11+); annotations were authored
    against `mypy --strict` in mind and are exercised at runtime by
    the test suite.
- **Blocked / next**:
  - Run `pytest`, `ruff`, `mypy` on a 3.11+ environment in CI to
    confirm the broader project suite still passes.
  - Optional follow-up: a small `mypy.ini` override or a
    `tests/cursor_harness/test_router_typing.py` driver that runs
    `mypy --strict` on the hooks dir, once a 3.11 venv is available.

## 2026-04-25 — Initial scaffolding

- **Agent**: Human + scaffolding agent
- **Goal**: Stand up the repository skeleton, rules, agent definitions, and a
  modular Python package layout for the full pipeline.
- **Done**:
  - Created repo structure (`data/`, `research/`, `strategies/`, `risk/`,
    `backtests/`, `execution/`, `monitoring/`, `docs/`, `configs/`, `tests/`).
  - Wrote `.cursor/rules/` (architecture, coding-standards, research-workflow,
    backtesting).
  - Wrote `AGENTS.md`, `TODO.md`, `DECISIONS.md`, `SIGNALS.md`,
    `docs/DESIGN.md`, `docs/STRATEGY.md`.
  - Wrote skeleton modules (interfaces + stubs) for each pipeline stage.
  - `pyproject.toml` with the agreed stack.
- **Verified**: `python -c "import data, research, strategies, risk, backtests, execution, monitoring"` imports without error.
- **Blocked / next**: Begin Milestone 1 — data ingestion (`data/ingest/binance.py`).
