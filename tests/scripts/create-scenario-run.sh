#!/usr/bin/env bash
set -euo pipefail

tests_dir="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
runs_dir="$tests_dir/runs"
scenario="${1:?Usage: create-scenario-run.sh SCENARIO}"

if [ ! -d "$tests_dir/scenarios/$scenario" ] || [ "$(basename -- "$scenario")" != "$scenario" ]; then
  printf 'Unknown scenario: %s\n' "$scenario" >&2
  exit 1
fi

mkdir -p "$runs_dir"
run_root="$runs_dir/$(date +%Y%m%d-%H%M)-$scenario"
mkdir "$run_root"
mkdir -p \
  "$run_root/claude-config" \
  "$run_root/logs" \
  "$run_root/prompts" \
  "$run_root/sources" \
  "$run_root/vault"

printf '%s\n' "$run_root"
