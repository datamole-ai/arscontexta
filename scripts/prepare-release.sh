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

  case "$(convco version --prefix '' --bump --label --config .github/versionrc)" in
    release) echo "there are no releasable conventional commits"; return ;;
    major) bump=minor ;;
    *) bump=patch ;;
  esac

  version="$(convco version --prefix '' "--$bump")"
  plugin_json="$(jq --arg version "$version" '.version = $version' .claude-plugin/plugin.json)"
  vault_json="$(jq --arg version "$version" '{version: $version}' template/.second-brain)"
  printf '%s\n' "$plugin_json" > .claude-plugin/plugin.json
  printf '%s\n' "$vault_json" > template/.second-brain
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
