#!/usr/bin/env python3
"""Build the EnvBoard sample app for one environment.

Usage:
    python3 scripts/build.py --config config/staging.env --out dist

Reads KEY=VALUE pairs from the given config file, renders app/template.html
with those values (plus the announcement and build information) into
<out>/index.html, and writes the resolved configuration to <out>/config.json
so it can be inspected and smoke-tested.
"""
import argparse, json, os, subprocess, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_env_file(path):
    cfg = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    return cfg


def git_value(*args, fallback):
    try:
        return subprocess.check_output(["git", "-C", ROOT, *args], text=True).strip() or fallback
    except Exception:
        return fallback


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True, help="path to the environment config file")
    ap.add_argument("--out", default="dist", help="output directory")
    args = ap.parse_args()

    cfg_path = os.path.join(ROOT, args.config) if not os.path.isabs(args.config) else args.config
    cfg = read_env_file(cfg_path)

    with open(os.path.join(ROOT, "app", "template.html")) as f:
        html = f.read()
    with open(os.path.join(ROOT, "app", "announcement.txt")) as f:
        announcement = f.read().strip()

    build = {
        "BUILD_BRANCH": os.environ.get("GITHUB_REF_NAME") or git_value("rev-parse", "--abbrev-ref", "HEAD", fallback="local"),
        "BUILD_COMMIT": os.environ.get("GITHUB_SHA", "")[:7] or git_value("rev-parse", "--short", "HEAD", fallback="local"),
        "BUILD_TIME": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "CONFIG_FILE": args.config,
        "ANNOUNCEMENT": announcement,
    }
    values = {**cfg, **build}
    for key, val in values.items():
        html = html.replace("{{" + key + "}}", val)

    leftover = [p for p in html.split("{{")[1:]]
    missing = [p.split("}}")[0] for p in leftover if "}}" in p]
    if missing:
        print("ERROR: unresolved placeholders:", ", ".join(sorted(set(missing))), file=sys.stderr)
        return 1

    out_dir = os.path.join(ROOT, args.out)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(html)
    with open(os.path.join(out_dir, "config.json"), "w") as f:
        json.dump({**cfg, **build}, f, indent=2)

    print(f"Built {cfg.get('APP_ENV', '?')} build from {args.config} -> {args.out}/index.html")
    print(f"  branch={build['BUILD_BRANCH']} commit={build['BUILD_COMMIT']} api={cfg.get('API_BASE_URL')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
