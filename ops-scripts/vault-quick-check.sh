#!/usr/bin/env bash
# vault-quick-check.sh — verify required vault structure.
# Output: single-line JSON. Exit 0 if ok=true, 1 if errors found.
# Bash 3.2 compatible (no set -u + arrays).

errors=()
warnings=()

add_err() { errors=("${errors[@]}" "$1"); }
add_warn() { warnings=("${warnings[@]}" "$1"); }

# Vault marker
[ -f .arscontexta ] || add_err "missing .arscontexta vault marker"

# Required directories
[ -d ops ]            || add_err "missing ops/"
[ -d ops/queue ]      || add_err "missing ops/queue/"
[ -d ops/templates ]  || add_err "missing ops/templates/"
[ -d ops/scripts ]    || add_err "missing ops/scripts/"
[ -d self ]           || add_err "missing self/"
[ -d .claude/skills ] || add_err "missing .claude/skills/"

# Required files
[ -f ops/queue/queue.json ]       || add_err "missing ops/queue/queue.json"
[ -f ops/derivation-manifest.md ] || add_err "missing ops/derivation-manifest.md"

# queue.json shape
if [ -f ops/queue/queue.json ]; then
  if ! jq empty ops/queue/queue.json 2>/dev/null; then
    add_err "ops/queue/queue.json is not valid JSON"
  elif ! jq -e '.tasks | type == "array"' ops/queue/queue.json >/dev/null 2>&1; then
    add_err "ops/queue/queue.json missing .tasks array"
  fi
fi

# YAML scalar lookup: read first occurrence of `key: value` (with optional
# quotes) inside the manifest. Tolerates indentation under `vocabulary:`.
yaml_get() {
  local key="$1" file="$2"
  [ -f "$file" ] || return 1
  awk -v key="$key" '
    BEGIN { found = 0 }
    {
      line = $0
      sub(/^[[:space:]]+/, "", line)
      if (match(line, "^" key ":[[:space:]]*")) {
        val = substr(line, RLENGTH + 1)
        sub(/[[:space:]]*#.*$/, "", val)
        sub(/^"/, "", val); sub(/"$/, "", val)
        sub(/^'\''/, "", val); sub(/'\''$/, "", val)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", val)
        if (val != "") { print val; found = 1; exit }
      }
    }
    END { exit !found }
  ' "$file"
}

# Notes/inbox directories from manifest (warn-level — folder may exist under
# a different name than the manifest declares; either way the manifest is the
# source of truth).
if [ -f ops/derivation-manifest.md ]; then
  notes_dir=$(yaml_get note_collection ops/derivation-manifest.md 2>/dev/null \
    || yaml_get notes ops/derivation-manifest.md 2>/dev/null || echo "")
  inbox_dir=$(yaml_get inbox ops/derivation-manifest.md 2>/dev/null || echo "")
  [ -n "$notes_dir" ] && [ ! -d "$notes_dir" ] \
    && add_warn "notes directory '$notes_dir' (from manifest) does not exist"
  [ -n "$inbox_dir" ] && [ ! -d "$inbox_dir" ] \
    && add_warn "inbox directory '$inbox_dir' (from manifest) does not exist"
fi

# Build JSON payload
err_count="${#errors[@]}"
warn_count="${#warnings[@]}"

if [ "$err_count" -gt 0 ]; then
  err_json=$(printf '%s\n' "${errors[@]}" | jq -R -s -c 'split("\n") | map(select(. != ""))')
else
  err_json='[]'
fi

if [ "$warn_count" -gt 0 ]; then
  warn_json=$(printf '%s\n' "${warnings[@]}" | jq -R -s -c 'split("\n") | map(select(. != ""))')
else
  warn_json='[]'
fi

if [ "$err_count" -eq 0 ]; then
  ok=true
  exit_code=0
else
  ok=false
  exit_code=1
fi

jq -n --argjson ok "$ok" --argjson errors "$err_json" --argjson warnings "$warn_json" \
  '{ok:$ok, errors:$errors, warnings:$warnings}'

exit "$exit_code"
