#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
cd "$repo_root"

if [ -n "$(git status --porcelain --untracked-files=normal)" ]; then
  echo "release preparation requires a clean worktree" >&2
  exit 1
fi

export ROOSTER_NO_CACHE=1
current_version="$(uv version --short)"
first_version_tag="$(
  git tag --list \
    | sed -nE '/^[0-9]+\.[0-9]+\.[0-9]+$/p' \
    | sed -n '1p'
)"

if [ -z "$first_version_tag" ]; then
  if [ "$current_version" != "1.0.0" ]; then
    echo "the first release must start at 1.0.0, found $current_version" >&2
    exit 1
  fi
  uv run --python 3.12 python scripts/sync-generator-version.py --initial-changelog
else
  uv run --python 3.12 --group release rooster release
  uv run --python 3.12 python scripts/sync-generator-version.py
fi

new_version="$(uv version --short)"

case "$new_version" in
  [0-9]*.[0-9]*.[0-9]*) ;;
  *)
    echo "Rooster produced an invalid release version: $new_version" >&2
    exit 1
    ;;
esac

printf 'prepared %s\n' "$new_version"
