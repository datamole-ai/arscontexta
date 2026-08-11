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

if grep -R -n -E 'uv run --project ops/tooling[[:space:]]+vault' \
  "$repo_root/template/.claude/skills"; then
  echo "generated runtime commands must use uv run --locked" >&2
  exit 1
fi

(
  cd "$vault_root"
  uv run --project ops/tooling --locked vault validate --all
)

cmp "$repo_root/vault-tooling/uv.lock" "$vault_root/ops/tooling/uv.lock"
cp "$vault_root/ops/tooling/uv.lock" "$test_root/uv.lock.before-drift"
awk '
  !changed && $0 ~ /^version = "/ {
    print "version = \"999999.0.0\""
    changed = 1
    next
  }
  { print }
  END { if (!changed) exit 1 }
' "$vault_root/ops/tooling/pyproject.toml" > "$test_root/pyproject.toml.with-drift"
mv "$test_root/pyproject.toml.with-drift" "$vault_root/ops/tooling/pyproject.toml"

if ! grep -Fq 'version = "999999.0.0"' "$vault_root/ops/tooling/pyproject.toml"; then
  echo "failed to create project metadata drift for the lock check" >&2
  exit 1
fi

set +e
drift_output=$(
  cd "$vault_root"
  uv run --project ops/tooling --locked vault validate --all 2>&1
)
drift_status=$?
set -e

if [ "$drift_status" -eq 0 ]; then
  echo "uv run --locked accepted project metadata drift" >&2
  exit 1
fi

if ! cmp "$test_root/uv.lock.before-drift" "$vault_root/ops/tooling/uv.lock"; then
  echo "uv run --locked rewrote the copied lock after project metadata drift" >&2
  exit 1
fi

if [ -z "$drift_output" ]; then
  echo "uv run --locked failed without a diagnostic" >&2
  exit 1
fi
