#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"

main() {
  cd "$repo_root"

  if [ -n "$(git status --porcelain --untracked-files=normal)" ]; then
    echo "release preparation requires a clean worktree" >&2
    exit 1
  fi

  project_version="$(uv version --short)"
  released_version="$(convco version --prefix '' --config .github/versionrc)"

  if [ "$project_version" != "$released_version" ]; then
    echo "project version $project_version does not match release tag $released_version" >&2
    exit 1
  fi
  if [ "$(git rev-list --count "$released_version..HEAD")" -eq 0 ]; then
    echo "there are no commits to release after $released_version" >&2
    exit 1
  fi

  next_version="$(convco version --prefix '' --bump --config .github/versionrc)"
  if [ "$next_version" = "$released_version" ]; then
    uv version --bump patch
  else
    uv version "$next_version"
  fi

  uv run --python 3.12 python scripts/sync-generator-version.py
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
