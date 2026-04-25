# GitHub Pages documentation site

This folder is the **MkDocs source** for the public spec and project-docs site
(published via GitHub Actions, not from `main` until you choose to merge).

## Live site

**https://finalflick.github.io/market-prediction/**

## What gets published

At **build time**, `hooks/sync_sources.py` copies into `docsite/` (ephemeral,
gitignored except this README and other hand-authored files):

| Source | Destination |
| --- | --- |
| `specs/` | `docsite/specs/` |
| `docs/` | `docsite/docs/` |
| Selected root `*.md` (see hook) | `docsite/` |

The repo root **`README.md` is not copied** here, so this file stays the
**readme for the docs/Pages pipeline** without clashing with the product README.

## Local preview

From the repository root (same directory as `mkdocs.yml`):

```powershell
py -3.12 -m venv .venv-docs
.\.venv-docs\Scripts\Activate.ps1
pip install -r docsite/requirements.txt
mkdocs serve
```

Open **http://127.0.0.1:8000/**. Static output is written to `site/` (ignored by git).

## Deploy

- Workflow: [`.github/workflows/pages.yml`](../.github/workflows/pages.yml)
- One-time / troubleshooting: [`PAGE_DEPLOY.md`](PAGE_DEPLOY.md)

## Staying in sync with `main`

This work usually lives on branch **`experiment/specs-gh-pages`** in a sibling
worktree so frequent commits on `main` do not conflict. To refresh mirrored
content from `main`:

```bash
git fetch origin
git rebase origin/main   # or: git merge origin/main
git push
```

Pushes that touch `specs/**`, `docs/**`, matching root `*.md`, `mkdocs.yml`,
`docsite/**`, or the workflow file trigger a new Pages build (see workflow
`paths` filters).

## Customizing

- **Theme / palette:** [`stylesheets/extra.css`](stylesheets/extra.css)
- **Home page:** [`index.md`](index.md)
- **Mermaid init:** [`javascripts/mermaid-init.js`](javascripts/mermaid-init.js)
- **Pinned Python deps:** [`requirements.txt`](requirements.txt) (not in `pyproject.toml`)
