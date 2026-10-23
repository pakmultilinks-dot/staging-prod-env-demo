# Runbook: how a change moves from staging to production

This is the operating guide for the EnvBoard two-environment setup.
Repository layout and local commands are in [README.md](README.md).

## 1. The environments

| | Staging | Production |
|---|---|---|
| Purpose | Test changes safely before customers see them | The live service customers use |
| Branch | `staging` | `main` |
| Workflow | `.github/workflows/deploy-staging.yml` | `.github/workflows/deploy-production.yml` |
| Config | `config/staging.env` | `config/production.env` |
| URL | `https://pakmultilinks-dot.github.io/staging-prod-env-demo/staging/` | `https://pakmultilinks-dot.github.io/staging-prod-env-demo/` |
| Data | Test data only | Real data |

Rule of thumb: **code flows `staging` first, then `main`. Config never
flows**: each environment keeps its own config file, and a merge must never
copy staging values into `config/production.env`.

## 2. Shipping a change, step by step

1. **Work on the `staging` branch.**
   `git checkout staging`, make the change, commit, `git push`.
   (For team work, branch off `staging`, then merge back into `staging`.)
2. **Watch the staging deploy.** The "Deploy to STAGING" workflow builds the
   app with `config/staging.env` and runs the smoke test. If the smoke test
   fails, nothing is published and production is untouched.
3. **Verify on the staging URL.** Open the staging URL and check the change
   works and the page still shows the staging banner and staging values.
   The build-information table on the page shows the commit that is live.
4. **Promote: open a pull request from `staging` into `main`.**
   The "Validate" workflow builds and smoke tests **both** configurations
   on the pull request. Review the diff, paying special attention to
   `config/production.env`: it should change only if the change is
   deliberately a production config change.
5. **Merge the pull request.** Merging into `main` triggers the
   "Deploy to PRODUCTION" workflow, which rebuilds with
   `config/production.env`, smoke tests (including a check that a
   production build never points at a staging API URL), and publishes.
6. **Verify on the production URL.** Confirm the change is live, the banner
   shows production values, and the build-information table shows the merge
   commit. The announcement content should now match what was tested on
   staging, while every config value stays the production one.

## 3. Changing a configuration value

- Edit **only** the file for the environment you mean to change
  (`config/staging.env` or `config/production.env`), on that environment's
  branch, and let the normal flow redeploy it.
- A production-only config change can go straight through a small pull
  request into `main`, but it still gets the Validate workflow and the
  production smoke test before it publishes.
- Add a new value in three places: both config files (with the right value
  per environment) and the template or code that reads it. If a key is
  missing, the build fails with an "unresolved placeholders" error instead
  of silently shipping a broken page.

## 4. If something goes wrong (rollback)

- **Bad deploy on staging:** fix forward on `staging`, or
  `git revert <commit>` and push; staging redeploys automatically.
- **Bad deploy on production:** revert the merge commit on `main`
  (`git revert -m 1 <merge-sha>`) and push. The production workflow
  republishes the previous state. Never force-push `main`.
- **Workflow published but Pages looks stale:** check the Actions tab for
  the run result first; GitHub Pages can take a minute to refresh. The
  build-information table on the page (branch, commit, build time) tells
  you exactly which build is being served.

## 5. Secrets

- This repository contains **no secrets**. Config files hold public values
  only.
- A real secret (API key, token, password) goes in
  `GitHub repo > Settings > Environments > staging | production > Add secret`
  and is read in the workflow as `${{ secrets.NAME }}`. Secrets are scoped
  per environment, so staging credentials can never leak into a production
  deploy.
- If a secret is ever committed by mistake: rotate it immediately (assume
  it is public), then remove it from the code and from git history.

## 6. Who can do what (recommended branch protection)

- `main`: require a pull request, require the Validate workflow to pass,
  no direct pushes. This is what makes "everything on production was
  tested on staging first" a guarantee instead of a habit.
- `staging`: direct pushes allowed for the team, deploys are automatic.
