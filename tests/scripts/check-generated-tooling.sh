#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/../.." && pwd)"
test_parent="$(cd -- "${TMPDIR:-/tmp}" && pwd -P)"
test_root="$(mktemp -d "$test_parent/second-brain-tooling-check.XXXXXX")"
vault_root="$test_root/vault"

case "$test_root" in
  "$test_parent"/second-brain-tooling-check.*) ;;
  *)
    echo "unexpected temporary path: $test_root" >&2
    exit 1
    ;;
esac

if [ ! -d "$test_root" ] || [ -L "$test_root" ]; then
  echo "temporary test root must be a real directory: $test_root" >&2
  exit 1
fi

cleanup() {
  if [ -d "$test_root" ] && [ ! -L "$test_root" ]; then
    rm -rf -- "$test_root"
  fi
}
trap cleanup EXIT

mkdir "$vault_root"
bash "$repo_root/skills/setup/scripts/copy-template.sh" "$vault_root"

cmp "$repo_root/vault-tooling/uv.lock" "$vault_root/ops/tooling/uv.lock"

if grep -R -n -E '^[[:space:]]*uv[[:space:]]+lock([[:space:]]|$)' \
  "$repo_root/skills/setup"; then
  echo "setup must copy the reviewed lock instead of resolving one" >&2
  exit 1
fi

(
  cd "$vault_root"
  uv run --project ops/tooling vault validate --all
)

cmp "$repo_root/vault-tooling/uv.lock" "$vault_root/ops/tooling/uv.lock"
