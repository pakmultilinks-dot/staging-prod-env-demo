#!/usr/bin/env python3
"""Smoke test for a built deployment.

Usage:
    python3 scripts/smoke_test.py --expect-env staging --dir dist

Fails (exit 1) if dist/index.html or dist/config.json is missing, if the
resolved APP_ENV does not match the expected environment, or if the page
still contains unresolved template placeholders.
"""
import argparse, json, os, sys

ap = argparse.ArgumentParser()
ap.add_argument("--expect-env", required=True)
ap.add_argument("--dir", default="dist")
args = ap.parse_args()

failures = []

index_path = os.path.join(args.dir, "index.html")
cfg_path = os.path.join(args.dir, "config.json")

if not os.path.exists(index_path):
    failures.append("index.html missing")
else:
    html = open(index_path).read()
    if "{{" in html:
        failures.append("index.html still contains unresolved placeholders")

if not os.path.exists(cfg_path):
    failures.append("config.json missing")
    cfg = {}
else:
    cfg = json.load(open(cfg_path))
    if cfg.get("APP_ENV") != args.expect_env:
        failures.append(f"APP_ENV is {cfg.get('APP_ENV')!r}, expected {args.expect_env!r}")
    if args.expect_env == "production" and "staging" in str(cfg.get("API_BASE_URL", "")):
        failures.append("production build points at a staging API URL")

if failures:
    for f in failures:
        print("SMOKE TEST FAILED:", f)
    sys.exit(1)

print(f"SMOKE TEST PASSED: {args.expect_env} build OK (API {cfg.get('API_BASE_URL')}, log level {cfg.get('LOG_LEVEL')})")
