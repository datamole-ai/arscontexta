#!/usr/bin/env bash
set -euo pipefail

vault_root=${1:?Usage: copy-template.sh VAULT_ROOT}

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
plugin_root="$(cd -- "$script_dir/../../.." && pwd)"
tooling_dir="$plugin_root/vault-tooling"

cp -R "$plugin_root/template"/. "$vault_root"/

tar -C "$tooling_dir" --exclude '__pycache__' --exclude '*.py[co]' \
  -cf - pyproject.toml uv.lock src/vault |
  tar -xf - -C "$vault_root/ops/tooling"
