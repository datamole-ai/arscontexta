#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"

select_release_bump() {
  local released_version=$1
  local conventional_version=$2

  if [ "$conventional_version" = "$released_version" ]; then
    printf '%s\n' none
    return
  fi

  local released_major=${released_version%%.*}
  local conventional_major=${conventional_version%%.*}
  if [ "$conventional_major" != "$released_major" ]; then
    printf '%s\n' minor
  else
    printf '%s\n' patch
  fi
}

sync_generator_version() {
  local version=$1
  local plugin_json
  local vault_json

  plugin_json="$(jq --arg version "$version" '.version = $version' .claude-plugin/plugin.json)"
  vault_json="$(jq --arg version "$version" '.generator_version = $version' template/.second-brain)"
  printf '%s\n' "$plugin_json" > .claude-plugin/plugin.json
  printf '%s\n' "$vault_json" > template/.second-brain
}

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
  bump="$(select_release_bump "$released_version" "$next_version")"
  if [ "$bump" = none ]; then
    echo "there are no releasable conventional commits"
    return
  fi

  uv version --bump "$bump"
  sync_generator_version "$(uv version --short)"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
