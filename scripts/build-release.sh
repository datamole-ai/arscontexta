#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
output=${1:-dist/second-brain.zip}

plugin_version="$(
  uv run --python 3.12 python -c \
    'import json, pathlib, sys; print(json.loads(pathlib.Path(sys.argv[1]).read_text())["version"])' \
    "$repo_root/.claude-plugin/plugin.json"
)"

case "$output" in
  /*) ;;
  *) output="$repo_root/$output" ;;
esac

mkdir -p -- "$(dirname -- "$output")"
git -C "$repo_root" archive --format=zip --output "$output" HEAD -- \
  .claude-plugin/plugin.json \
  skills/setup/SKILL.md \
  skills/setup/scripts/copy-template.sh \
  template \
  vault-tooling/pyproject.toml \
  vault-tooling/uv.lock \
  vault-tooling/src/vault

unzip -tq "$output"
echo "built $output for plugin version $plugin_version"
