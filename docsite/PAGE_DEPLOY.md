# GitHub Pages — one-time setup (this branch)

The `pages` workflow uses `actions/deploy-pages@v4`, which **requires** the
`github-pages` environment. That environment may default to **only `main`**, so
deploys from `experiment/specs-gh-pages` can fail until you widen the rule.

## Steps (about 1 minute)

1. **Pages source**  
   Repository **Settings → Pages → Build and deployment → Source**  
   Select **GitHub Actions** (not “Deploy from a branch”).

2. **Allow this branch on the environment**  
   **Settings → Environments → `github-pages`**  
   Under **Deployment branches**, choose either:
   - **All branches**, or  
   - **Selected branches** → add `experiment/specs-gh-pages`.

3. **Re-run the workflow**  
   **Actions → `pages` →** re-run the latest failed run (or push an empty commit on
   this branch).

## Live URL

After a green run, the site is at:

`https://<user>.github.io/<repo>/`

For this repository: `https://finalflick.github.io/market-prediction/`

(Paths and casing follow GitHub’s project Pages URL rules.)
