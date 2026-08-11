#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
output=${1:-dist/second-brain.zip}

if ! git -C "$repo_root" diff --quiet HEAD --; then
  echo "release archive requires a clean tracked worktree" >&2
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
echo "built $output"
