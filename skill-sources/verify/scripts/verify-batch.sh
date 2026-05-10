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
SOURCE_INDEX=$(mktemp)
MOC_TARGETS=$(mktemp)
trap 'rm -f "$LINK_INDEX" "$SOURCE_INDEX" "$MOC_TARGETS"' EXIT

NOTES_DIR="$(awk -F'|' '
  /^[[:space:]]*note_collection:/ { sub(/.*:[[:space:]]*/, ""); print; exit }
  /^\|[[:space:]]*notes[[:space:]]*\|/ { v=$3; gsub(/^[[:space:]]+|[[:space:]]+$/, "", v); print v; exit }
' ops/derivation-manifest.md 2>/dev/null || true)"
[ -n "$NOTES_DIR" ] || NOTES_DIR="notes"

normalize() {
  printf '%s' "$1" \
    | sed -E 's/\|.*$//; s/#.*$//; s/\.md$//; s/^[[:space:]]+|[[:space:]]+$//g' \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//'
}

first_heading() {
  awk '/^# / { sub(/^# /, ""); print; exit }' "$1"
}

frontmatter_value() {
  local key="$1" file="$2"
  awk -v key="$key" '
    NR == 1 && $0 == "---" { fm=1; next }
    fm && $0 == "---" { exit }
    fm {
      pattern="^" key ":[[:space:]]*"
      if ($0 ~ pattern) {
        line=$0
        sub(pattern, "", line)
        gsub(/^["'\''[:space:]]+|["'\''[:space:]]+$/, "", line)
        print line
        exit
      }
    }
  ' "$file"
}

is_moc() {
  awk '
    /^---[[:space:]]*$/ { fm++; next }
    fm == 1 && /^content_type:[[:space:]]*moc[[:space:]]*$/ { found=1 }
    fm == 1 && /^tags:[[:space:]]*\[.*(moc|topic-map).*\]/ { found=1 }
    fm == 1 && /^[[:space:]]*-[[:space:]]*(moc|topic-map)[[:space:]]*$/ { found=1 }
    fm == 2 { exit }
    END { exit found ? 0 : 1 }
  ' "$1"
}

is_audit_exempt() {
  is_moc "$1" && return 0
  grep -qiE '^(audit|source_audit|audit_exempt):[[:space:]]*(template-example|example|exempt|system)' "$1" 2>/dev/null
}

is_source_path() {
  case "$1" in
    ops/queue/archive/*|*/ops/queue/archive/*|archive/*|*/archive/*) return 0 ;;
    *) return 1 ;;
  esac
}

index_key() {
  local index="$1" key="$2" path="$3" norm
  norm=$(normalize "$key")
  [ -n "$norm" ] && printf '%s\t%s\n' "$norm" "$path" >> "$index"
}

build_indexes() {
  : > "$LINK_INDEX"
  : > "$SOURCE_INDEX"

  while IFS= read -r file; do
    clean="${file#./}"
    kind="knowledge"
    is_source_path "$clean" && kind="source"

    index_key "$LINK_INDEX" "$(basename "$clean" .md)" "$clean"
    index_key "$LINK_INDEX" "$clean" "$clean"
    title=$(first_heading "$clean")
    [ -n "$title" ] && index_key "$LINK_INDEX" "$title" "$clean"

    if [ "$kind" = "source" ]; then
      index_key "$SOURCE_INDEX" "$(basename "$clean" .md)" "$clean"
      index_key "$SOURCE_INDEX" "$clean" "$clean"
      index_key "$SOURCE_INDEX" "$(basename "$(dirname "$clean")")" "$clean"
    fi
  done < <(find . -name "*.md" -type f -not -path "./.git/*" -print 2>/dev/null)

  jq -c '.tasks[]? | select(.type == "process" and (.source // "") != "")' "$QUEUE" 2>/dev/null |
    while IFS= read -r task; do
      id=$(echo "$task" | jq -r '.id')
      source=$(echo "$task" | jq -r '.source')
      [ -f "$source" ] || continue
      index_key "$SOURCE_INDEX" "source:$id" "$source"
      index_key "$LINK_INDEX" "source:$id" "$source"
    done

  find ops/queue/archive -name batch-manifest.json -type f 2>/dev/null |
    while IFS= read -r manifest; do
      jq -c 'select(.ok == true) | {batch, source}' "$manifest" 2>/dev/null |
        while IFS= read -r item; do
          id=$(echo "$item" | jq -r '.batch // empty')
          source=$(echo "$item" | jq -r '.source // empty')
          [ -n "$id" ] && [ -f "$source" ] || continue
          index_key "$SOURCE_INDEX" "source:$id" "$source"
          index_key "$LINK_INDEX" "source:$id" "$source"
        done
    done
}

resolve() {
  local index="$1" target="$2" norm
  norm=$(normalize "$target")
  [ -n "$norm" ] || return 1
  awk -F '\t' -v key="$norm" '$1 == key { print $2; exit }' "$index"
}

source_for_note() {
  local path="$1" target source
  target=$(grep -E '^Source:' "$path" 2>/dev/null | grep -oE '\[\[[^]]+\]\]' | head -1 | sed -E 's/^\[\[(.+)\]\]$/\1/' || true)
  if [ -n "$target" ]; then
    source=$(resolve "$SOURCE_INDEX" "$target")
    [ -n "$source" ] && { printf '%s' "$source"; return; }
  fi
  jq -r --arg b "$BATCH_ID" '[.tasks[] | select(.id == $b and .type == "process")] | first | .source // empty' "$QUEUE"
}

collect_moc_targets() {
  : > "$MOC_TARGETS"
  [ -d "$NOTES_DIR" ] || return
  while IFS= read -r file; do
    is_moc "$file" || continue
    grep -oE '\[\[[^]]+\]\]' "$file" 2>/dev/null |
      sed -E 's/^\[\[(.+)\]\]$/\1/' |
      while IFS= read -r target; do normalize "$target"; done
  done < <(find "$NOTES_DIR" -name "*.md" -type f 2>/dev/null) | sort -u > "$MOC_TARGETS"
}

json_lines_array() {
  printf '%s' "$1" | jq -s -c '.'
}

urls() {
  grep -Eo 'https?://[^[:space:])>]+' "$1" 2>/dev/null | sort -u || true
}

emails() {
  grep -Eio '[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}' "$1" 2>/dev/null | sort -u || true
}

source_audit_issues() {
  local path="$1" source="$2" cue source_count stated_count

  [ -f "$source" ] || { printf '%s\n' "source file unavailable"; return; }
  is_audit_exempt "$path" && return

  if ! grep -Eiq '\b(inference:|hypothesis|question|unknown|undefined|source (states|lists|marks|asks|does not state))\b' "$path"; then
    grep -Eio '\b(signals|implies|suggests|indicates|therefore|means|shows|proves|canonical|owned by)\b' "$path" 2>/dev/null |
      tr '[:upper:]' '[:lower:]' |
      sort -u |
      while IFS= read -r cue; do
        grep -Fqi "$cue" "$source" && continue
        printf 'unmarked inference cue: %s\n' "$cue"
      done
  fi

  if [ -n "$(urls "$source")" ] && grep -Eiq '\b(urls?|links?|repositories?|reports?|artifacts?)\b' "$path"; then
    urls "$source" | while IFS= read -r url; do
      [ -n "$url" ] || continue
      urls "$path" | grep -Fxq "$url" || printf 'source URL omitted: %s\n' "$url"
    done
  fi

  if [ -n "$(emails "$source")" ] && grep -Eiq '\b(contacts?|roster|emails?)\b' "$path"; then
    [ -n "$(emails "$path")" ] || grep -Eiq 'emails? (intentionally )?omitted|email addresses omitted' "$path" ||
      printf '%s\n' "source emails omitted without explicit omission note"
    source_count=$(emails "$source" | sed '/^$/d' | wc -l | tr -d ' ')
    stated_count=$(grep -Eio '\b[0-9]+[[:space:]]+(contacts?|people|emails?)\b' "$path" | head -1 | grep -Eo '[0-9]+' || true)
    [ -z "$stated_count" ] || [ "$stated_count" = "$source_count" ] ||
      printf 'email/contact count drift: source=%s note=%s\n' "$source_count" "$stated_count"
  fi
}

WORKLIST=$(jq -c --arg b "$BATCH_ID" '[.tasks[] | select(.batch == $b and .status == "pending" and .current_phase == "verify")]' "$QUEUE")
N=$(echo "$WORKLIST" | jq 'length')

echo "## Verify"
echo "**Batch:** $BATCH_ID"
echo "**Work-list:** $N entries"
echo ""

emit_machine() {
  jq -n \
    --arg batch "$BATCH_ID" \
    --argjson worklist "$N" \
    --arg link_status "$1" \
    --arg source_status "$2" \
    --arg orphan_status "$3" \
    --arg source_audit_status "$4" \
    --argjson links_scanned "$5" \
    --argjson broken_links "$6" \
    --argjson broken_sources "$7" \
    --argjson source_issues "$8" \
    --argjson orphans "$9" \
    --argjson per_note "${10}" \
    '{
      batch: $batch,
      worklist: $worklist,
      link_health: {status:$link_status, scanned:$links_scanned, broken:$broken_links},
      source_links: {status:$source_status, broken:$broken_sources},
      source_audit: {status:$source_audit_status, issues:$source_issues},
      orphan_check: {status:$orphan_status, count:($orphans | length), ids:$orphans},
      per_note: $per_note
    }'
}

if [ "$N" -eq 0 ]; then
  echo "### Per-note structural results"
  echo "- (none)"
  echo ""
  echo "### Vault-scope checks"
  echo "- Link health: SKIP"
  echo "- Source links: SKIP"
  echo "- Orphan check: SKIP"
  echo "- Source audit: SKIP"
  echo ""
  echo "### Machine output"
  emit_machine SKIP SKIP SKIP SKIP 0 '[]' '[]' '[]' '[]' '[]'
  exit 0
fi

build_indexes
collect_moc_targets

links_scanned=0
broken_links_jsonl=""
broken_sources_jsonl=""
orphans_jsonl=""
per_note_jsonl=""
source_issues_jsonl=""

echo "### Per-note structural results"
while IFS= read -r entry; do
  id=$(echo "$entry" | jq -r '.id')
  path=$(echo "$entry" | jq -r '.target_path')
  gran=$(echo "$entry" | jq -r '.granularity')
  issues=()

  if [ ! -f "$path" ]; then
    issues+=("file not found")
    per_note_jsonl="${per_note_jsonl}$(jq -nc --arg id "$id" --arg path "$path" --arg gran "$gran" '{id:$id,path:$path,granularity:$gran,validate:"FAIL",issues:["file not found"],review:"TBD"}')"$'\n'
    echo "- $id ($path) - Validate: FAIL (file not found); Review: TBD"
    continue
  fi

  while IFS= read -r row; do
    line_no="${row%%:*}"
    link="${row#*:}"
    target=$(printf '%s' "$link" | sed -E 's/^\[\[(.+)\]\]$/\1/')
    line=$(sed -n "${line_no}p" "$path")
    links_scanned=$((links_scanned + 1))
    if printf '%s' "$line" | grep -qE '^Source:'; then
      [ -n "$(resolve "$SOURCE_INDEX" "$target")" ] ||
        broken_sources_jsonl="${broken_sources_jsonl}$(jq -nc --arg id "$id" --arg target "$target" '{id:$id,target:$target}')"$'\n'
    else
      [ -n "$(resolve "$LINK_INDEX" "$target")" ] ||
        broken_links_jsonl="${broken_links_jsonl}$(jq -nc --arg id "$id" --arg target "$target" '{id:$id,target:$target}')"$'\n'
    fi
  done < <(grep -n -oE '\[\[[^]]+\]\]' "$path" 2>/dev/null)

  [ "$(head -1 "$path")" = "---" ] || issues+=("missing opening frontmatter delimiter")
  [ "$(grep -c '^---$' "$path")" -ge 2 ] || issues+=("missing closing frontmatter delimiter")
  desc=$(frontmatter_value description "$path")
  [ -n "$desc" ] || issues+=("missing description")
  printf '%s' "$desc" | grep -qE '\.$' && issues+=("trailing period on description")
  grep -qE '^Topics:' "$path" || issues+=("missing Topics footer")

  if [ "$gran" = "structure" ]; then
    grep -qE '^Source:' "$path" || issues+=("missing Source footer")
    source=$(source_for_note "$path")
    while IFS= read -r issue; do
      [ -n "$issue" ] || continue
      issues+=("$issue")
      source_issues_jsonl="${source_issues_jsonl}$(jq -nc --arg id "$id" --arg path "$path" --arg source "$source" --arg issue "$issue" '{id:$id,target_path:$path,source:$source,issue:$issue}')"$'\n'
    done < <(source_audit_issues "$path" "$source")
  fi

  if [ "$gran" = "capture" ] && ! grep -q '^```' "$path"; then
    issues+=("missing fenced verbatim block")
  fi

  if ! is_moc "$path"; then
    bn=$(normalize "$(basename "$path" .md)")
    title=$(normalize "$(first_heading "$path")")
    if ! grep -Fxq "$bn" "$MOC_TARGETS" && { [ -z "$title" ] || ! grep -Fxq "$title" "$MOC_TARGETS"; }; then
      orphans_jsonl="${orphans_jsonl}$(jq -nc --arg id "$id" --arg path "$path" '{id:$id,target_path:$path}')"$'\n'
    fi
  fi

  if [ "${#issues[@]}" -eq 0 ]; then
    verdict="PASS"
    issues_json='[]'
    detail=""
  elif [ "${#issues[@]}" -eq 1 ] && [ "${issues[0]}" = "trailing period on description" ]; then
    verdict="WARN"
    issues_json=$(printf '%s\n' "${issues[@]}" | jq -R -s -c 'split("\n") | map(select(. != ""))')
    detail=" (${issues[*]})"
  else
    verdict="FAIL"
    issues_json=$(printf '%s\n' "${issues[@]}" | jq -R -s -c 'split("\n") | map(select(. != ""))')
    detail=" ($(IFS=, ; echo "${issues[*]}"))"
  fi

  echo "- $id ($path) - Validate: ${verdict}${detail}; Review: TBD"
  per_note_jsonl="${per_note_jsonl}$(jq -nc --arg id "$id" --arg path "$path" --arg gran "$gran" --arg verdict "$verdict" --argjson issues "$issues_json" '{id:$id,path:$path,granularity:$gran,validate:$verdict,issues:$issues,review:"TBD"}')"$'\n'
done < <(echo "$WORKLIST" | jq -c '.[]')

broken_links=$(json_lines_array "$broken_links_jsonl")
broken_sources=$(json_lines_array "$broken_sources_jsonl")
orphans=$(json_lines_array "$orphans_jsonl")
source_issues=$(json_lines_array "$source_issues_jsonl")
per_note=$(json_lines_array "$per_note_jsonl")

[ "$(echo "$broken_links" | jq 'length')" -eq 0 ] && link_status="PASS" || link_status="FAIL"
[ "$(echo "$broken_sources" | jq 'length')" -eq 0 ] && source_status="PASS" || source_status="FAIL"
[ "$(echo "$orphans" | jq 'length')" -eq 0 ] && orphan_status="PASS" || orphan_status="FAIL"
[ "$(echo "$source_issues" | jq 'length')" -eq 0 ] && source_audit_status="PASS" || source_audit_status="FAIL"

echo ""
echo "### Vault-scope checks"
echo "- Link health: $link_status ($links_scanned links scanned, $(echo "$broken_links" | jq 'length') broken)"
echo "- Source links: $source_status ($(echo "$broken_sources" | jq 'length') broken)"
echo "- Orphan check: $orphan_status ($(echo "$orphans" | jq 'length') orphans found)"
echo "- Source audit: $source_audit_status ($(echo "$source_issues" | jq 'length') issues found)"
echo ""
echo "### Machine output"
emit_machine "$link_status" "$source_status" "$orphan_status" "$source_audit_status" "$links_scanned" "$broken_links" "$broken_sources" "$source_issues" "$orphans" "$per_note"
