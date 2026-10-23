# Staging and Production Environments: EnvBoard (sample app)

A small sample web app ("EnvBoard") deployed to **two separate environments**,
each fed by its **own branch** and its **own configuration**, with the full
promotion path documented in [RUNBOOK.md](RUNBOOK.md).

## Live deployments

| Environment | Source branch | Config file | URL |
|---|---|---|---|
| Staging | `staging` | `config/staging.env` | https://pakmultilinks-dot.github.io/staging-prod-env-demo/staging/ |
| Production | `main` | `config/production.env` | https://pakmultilinks-dot.github.io/staging-prod-env-demo/ |

Open both URLs side by side: the banner colour, banner text, API base URL,
feature flags, log level, support email and session timeout all differ,
because each deployment is built from its own config file. The page footer
of each build also shows which branch and commit it was built from.

## How it works

- `app/` holds the app source (an HTML template plus the announcement text).
- `config/staging.env` and `config/production.env` hold the per-environment
  values (non-secret only, see "Secrets" below).
- `scripts/build.py --config <file> --out dist` renders the app with one
  environment's values and writes `dist/index.html` plus `dist/config.json`.
- `scripts/smoke_test.py --expect-env <env> --dir dist` verifies a build
  really carries the intended environment before anything is published.
- `.github/workflows/deploy-staging.yml` runs **only** on pushes to the
  `staging` branch: build with the staging config, smoke test, publish to
  GitHub Pages under `/staging/`.
- `.github/workflows/deploy-production.yml` runs **only** on pushes to the
  `main` branch: build with the production config, smoke test, publish to
  GitHub Pages at the site root.
- `.github/workflows/validate.yml` runs on pull requests into `main` and
  builds and smoke tests **both** configurations without deploying.

## Run it locally

```bash
python3 scripts/build.py --config config/staging.env --out dist
python3 scripts/smoke_test.py --expect-env staging --dir dist
python3 -m http.server 8080 --directory dist   # then open http://localhost:8080
```

Swap `staging.env` for `production.env` to preview the production build.

## Secrets

There are **no secrets in this repository**, by design. The config files
contain only public, non-sensitive values (URLs, flags, display text). Any
real credential (API keys, tokens, passwords) must be stored as a GitHub
Environment secret (`Settings > Environments > staging / production`) and
referenced from the workflow, never committed. See RUNBOOK.md, section 5.
