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

sync_product_version() {
  local version=$1
  local plugin_json
  local vault_json

  plugin_json="$(jq --arg version "$version" '.version = $version' .claude-plugin/plugin.json)"
  vault_json="$(jq --arg version "$version" '{version: $version}' template/.second-brain)"

  uv version --project vault-tooling --no-sync "$version"
  printf '%s\n' "$plugin_json" > .claude-plugin/plugin.json
  printf '%s\n' "$vault_json" > template/.second-brain
}

increment_version() {
  local version=$1
  local bump=$2

  if [[ ! "$version" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
    echo "plugin version must use X.Y.Z format: $version" >&2
    return 1
  fi

  local major=${BASH_REMATCH[1]}
  local minor=${BASH_REMATCH[2]}
  local patch=${BASH_REMATCH[3]}

  case "$bump" in
    minor) printf '%s.%s.0\n' "$major" "$((minor + 1))" ;;
    patch) printf '%s.%s.%s\n' "$major" "$minor" "$((patch + 1))" ;;
    *)
      echo "unsupported release bump: $bump" >&2
      return 1
      ;;
  esac
}

main() {
  cd "$repo_root"

  if [ -n "$(git status --porcelain --untracked-files=normal)" ]; then
    echo "release preparation requires a clean worktree" >&2
    exit 1
  fi

  product_version="$(jq -er '.version | select(type == "string")' .claude-plugin/plugin.json)"
  released_version="$(convco version --prefix '' --config .github/versionrc)"

  if [ "$product_version" != "$released_version" ]; then
    echo "plugin version $product_version does not match release tag $released_version" >&2
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

  sync_product_version "$(increment_version "$product_version" "$bump")"
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
