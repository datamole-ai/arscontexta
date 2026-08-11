#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
output=${1:-dist/second-brain.zip}
release_tag=${RELEASE_TAG:-}

plugin_version="$(
  uv run --python 3.12 python -c \
    'import json, pathlib, sys; print(json.loads(pathlib.Path(sys.argv[1]).read_text())["version"])' \
    "$repo_root/.claude-plugin/plugin.json"
)"

if [ -n "$release_tag" ] && [ "$release_tag" != "v$plugin_version" ]; then
  echo "release tag $release_tag does not match plugin version $plugin_version" >&2
  exit 1
fi

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
