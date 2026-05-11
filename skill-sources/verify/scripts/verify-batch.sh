#!/usr/bin/env bash
# Ars Contexta - Verify batch structural checks.
# Args: BATCH_ID
# Output: compact human report + machine JSON consumed by /verify.

set -e

BATCH_ID="${1:-}"
if [ -z "$BATCH_ID" ]; then
  echo "ERROR: verify-batch.sh requires BATCH_ID" >&2
  exit 1
fi

QUEUE="ops/queue/queue.json"
[ -f "$QUEUE" ] || { echo "ERROR: $QUEUE not found" >&2; exit 1; }

LINK_INDEX=$(mktemp)
trap 'rm -f "$LINK_INDEX"' EXIT

NOTES_DIR="$(awk -F'|' '
  /^[[:space:]]*note_collection:/ { sub(/.*:[[:space:]]*/, ""); print; exit }
  /^\|[[:space:]]*notes[[:space:]]*\|/ { v=$3; gsub(/^[[:space:]]+|[[:space:]]+$/, "", v); print v; exit }
' ops/derivation-manifest.md 2>/dev/null || true)"
[ -n "$NOTES_DIR" ] || NOTES_DIR="notes"

normalize() {
  local target="$1"

  target="${target%%|*}"
  target="${target%%#*}"
  target="${target%.md}"
  target="${target##*/}"

  printf '%s' "$target" \
    | sed -E 's/^[[:space:]]+|[[:space:]]+$//g' \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'
}

json_lines_array() {
  printf '%s' "$1" | jq -s -c '.'
}

frontmatter_field_exists() {
  local key="$1" file="$2"

  awk -v key="$key" '
    NR == 1 && $0 == "---" { fm=1; next }
    fm && $0 == "---" { exit }
    fm {
      pattern="^" key ":[[:space:]]*"
      if ($0 ~ pattern) { found=1; exit }
    }
    END { exit found ? 0 : 1 }
  ' "$file"
}

build_link_index() {
  : > "$LINK_INDEX"
  [ -d "$NOTES_DIR" ] || return

  while IFS= read -r file; do
    key=$(normalize "$(basename "$file" .md)")
    [ -n "$key" ] && printf '%s\t%s\n' "$key" "$file" >> "$LINK_INDEX"
  done < <(find "$NOTES_DIR" -name "*.md" -type f 2>/dev/null)
}

link_exists() {
  local target="$1" key

  key=$(normalize "$target")
  [ -n "$key" ] || return 1
  awk -F '\t' -v key="$key" '$1 == key { found=1; exit } END { exit found ? 0 : 1 }' "$LINK_INDEX"
}

emit_machine() {
  local frontmatter_status="$1"
  local wiki_status="$2"
  local links_scanned="$3"
  local frontmatter_issues="$4"
  local broken_links="$5"
  local alias_links="$6"
  local per_note="$7"

  jq -n \
    --arg batch "$BATCH_ID" \
    --argjson worklist "$N" \
    --arg frontmatter_status "$frontmatter_status" \
    --arg wiki_status "$wiki_status" \
    --argjson links_scanned "$links_scanned" \
    --argjson frontmatter_issues "$frontmatter_issues" \
    --argjson broken_links "$broken_links" \
    --argjson alias_links "$alias_links" \
    --argjson per_note "$per_note" \
    '{
      batch: $batch,
      worklist: $worklist,
      checks: {
        frontmatter: {status: $frontmatter_status, issues: $frontmatter_issues},
        wiki_links: {status: $wiki_status, scanned: $links_scanned, broken: $broken_links, aliases: $alias_links}
      },
      per_note: $per_note
    }'
}

WORKLIST=$(jq -c --arg b "$BATCH_ID" '[.tasks[] | select(.batch == $b and .status == "pending" and .current_phase == "verify")]' "$QUEUE")
N=$(echo "$WORKLIST" | jq 'length')

echo "## Verify"
echo "**Batch:** $BATCH_ID"
echo "**Work-list:** $N entries"
echo ""

if [ "$N" -eq 0 ]; then
  echo "### Per-note structural results"
  echo "- (none)"
  echo ""
  echo "### Checks"
  echo "- Frontmatter: SKIP"
  echo "- Wiki links: SKIP"
  echo ""
  echo "### Machine output"
  emit_machine SKIP SKIP 0 '[]' '[]' '[]' '[]'
  exit 0
fi

build_link_index

links_scanned=0
frontmatter_issues_jsonl=""
broken_links_jsonl=""
alias_links_jsonl=""
per_note_jsonl=""

echo "### Per-note structural results"
while IFS= read -r entry; do
  id=$(echo "$entry" | jq -r '.id')
  path=$(echo "$entry" | jq -r '.target_path')
  issues=()

  if [ ! -f "$path" ]; then
    issues+=("file not found")
    frontmatter_issues_jsonl="${frontmatter_issues_jsonl}$(jq -nc --arg id "$id" --arg path "$path" --arg issue "file not found" '{id:$id,path:$path,issue:$issue}')"$'\n'
  else
    if [ "$(head -n 1 "$path")" != "---" ]; then
      issues+=("missing opening frontmatter delimiter")
      frontmatter_issues_jsonl="${frontmatter_issues_jsonl}$(jq -nc --arg id "$id" --arg path "$path" --arg issue "missing opening frontmatter delimiter" '{id:$id,path:$path,issue:$issue}')"$'\n'
    fi

    if [ "$(grep -c '^---$' "$path")" -lt 2 ]; then
      issues+=("missing closing frontmatter delimiter")
      frontmatter_issues_jsonl="${frontmatter_issues_jsonl}$(jq -nc --arg id "$id" --arg path "$path" --arg issue "missing closing frontmatter delimiter" '{id:$id,path:$path,issue:$issue}')"$'\n'
    fi

    if ! frontmatter_field_exists description "$path"; then
      issues+=("missing description")
      frontmatter_issues_jsonl="${frontmatter_issues_jsonl}$(jq -nc --arg id "$id" --arg path "$path" --arg issue "missing description" '{id:$id,path:$path,issue:$issue}')"$'\n'
    fi

    if ! frontmatter_field_exists tags "$path"; then
      issues+=("missing tags")
      frontmatter_issues_jsonl="${frontmatter_issues_jsonl}$(jq -nc --arg id "$id" --arg path "$path" --arg issue "missing tags" '{id:$id,path:$path,issue:$issue}')"$'\n'
    fi

    while IFS= read -r link; do
      target="${link#\[\[}"
      target="${target%\]\]}"

      if printf '%s' "$target" | grep -q '|'; then
        issues+=("alias wiki link: $target")
        alias_links_jsonl="${alias_links_jsonl}$(jq -nc --arg id "$id" --arg path "$path" --arg target "$target" '{id:$id,path:$path,target:$target}')"$'\n'
        continue
      fi

      case "$target" in
        source:*) continue ;;
      esac

      links_scanned=$((links_scanned + 1))
      if ! link_exists "$target"; then
        issues+=("broken wiki link: $target")
        broken_links_jsonl="${broken_links_jsonl}$(jq -nc --arg id "$id" --arg path "$path" --arg target "$target" '{id:$id,path:$path,target:$target}')"$'\n'
      fi
    done < <(grep -oE '\[\[[^]]+\]\]' "$path" 2>/dev/null || true)
  fi

  if [ "${#issues[@]}" -eq 0 ]; then
    verdict="PASS"
    issues_json='[]'
    detail=""
  else
    verdict="FAIL"
    issues_json=$(printf '%s\n' "${issues[@]}" | jq -R -s -c 'split("\n") | map(select(. != ""))')
    detail=" ($(IFS=, ; echo "${issues[*]}"))"
  fi

  echo "- $id ($path) - Validate: ${verdict}${detail}"
  per_note_jsonl="${per_note_jsonl}$(jq -nc --arg id "$id" --arg path "$path" --arg verdict "$verdict" --argjson issues "$issues_json" '{id:$id,path:$path,validate:$verdict,issues:$issues}')"$'\n'
done < <(echo "$WORKLIST" | jq -c '.[]')

frontmatter_issues=$(json_lines_array "$frontmatter_issues_jsonl")
broken_links=$(json_lines_array "$broken_links_jsonl")
alias_links=$(json_lines_array "$alias_links_jsonl")
per_note=$(json_lines_array "$per_note_jsonl")

[ "$(echo "$frontmatter_issues" | jq 'length')" -eq 0 ] && frontmatter_status="PASS" || frontmatter_status="FAIL"
if [ "$(echo "$broken_links" | jq 'length')" -eq 0 ] && [ "$(echo "$alias_links" | jq 'length')" -eq 0 ]; then
  wiki_status="PASS"
else
  wiki_status="FAIL"
fi

echo ""
echo "### Checks"
echo "- Frontmatter: $frontmatter_status ($(echo "$frontmatter_issues" | jq 'length') issues)"
echo "- Wiki links: $wiki_status ($links_scanned links scanned, $(echo "$broken_links" | jq 'length') broken, $(echo "$alias_links" | jq 'length') aliases)"
echo ""
echo "### Machine output"
emit_machine "$frontmatter_status" "$wiki_status" "$links_scanned" "$frontmatter_issues" "$broken_links" "$alias_links" "$per_note"
