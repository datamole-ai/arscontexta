#!/bin/bash
# Ars Contexta — Verify (batch phase)
# Args: BATCH_ID
# Output: ## Verify human-readable block (vault-scope checks + per-note
# structural results) followed by a `### Machine output` JSON object that
# orchestrators and the verify skill consume. Per-note Review verdicts stay
# at "TBD" — the LLM fills them in.
set -e

BATCH_ID="${1:-}"
if [ -z "$BATCH_ID" ]; then
  echo "ERROR: verify-batch.sh requires BATCH_ID" >&2
  exit 1
fi

# ── Vocabulary loader ──────────────────────────────────────────
NOTES_DIR="notes"
if [ -f ops/derivation-manifest.md ]; then
  while IFS='|' read -r _ universal domain _; do
    universal=$(echo "$universal" | xargs)
    domain=$(echo "$domain" | xargs)
    [ "$universal" = "notes" ] && NOTES_DIR="$domain"
  done < <(grep -E '^\| notes ' ops/derivation-manifest.md 2>/dev/null || true)
fi

# ── MOC helpers ────────────────────────────────────────────────
# A file counts as a topic map if its YAML frontmatter sets
# content_type: moc OR carries a tag of "moc" or "topic-map" (block-style
# `- moc` / `- topic-map` or inline `tags: [..., moc, ...]`).
is_moc_file() {
  awk '
    BEGIN { fm = 0; found = 0 }
    /^---[[:space:]]*$/ { fm++; if (fm == 2) exit; next }
    fm == 1 {
      if ($0 ~ /^content_type:[[:space:]]*moc[[:space:]]*$/) { found = 1; exit }
      if ($0 ~ /^[[:space:]]*-[[:space:]]*(moc|topic-map)[[:space:]]*$/) { found = 1; exit }
      if ($0 ~ /^tags:[[:space:]]*\[.*(moc|topic-map).*\]/) { found = 1; exit }
    }
    END { exit !found }
  ' "$1"
}

# Build the deduped set of every wiki-link target that appears inside a topic
# map's body. Filenames === titles verbatim, so targets compare directly to
# basenames without normalization.
collect_moc_link_targets() {
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    is_moc_file "$f" || continue
    grep -oE '\[\[[^]]+\]\]' "$f" 2>/dev/null \
      | sed -E 's/^\[\[(.+)\]\]$/\1/'
  done < <(find "$NOTES_DIR" -name "*.md" -type f 2>/dev/null) \
    | sort -u
}

# ── Work-list discovery ────────────────────────────────────────
if [ ! -f ops/queue/queue.json ]; then
  echo "ERROR: ops/queue/queue.json not found" >&2
  exit 1
fi
WORKLIST=$(jq -c --arg b "$BATCH_ID" \
  '[.tasks[] | select(.batch == $b and .status == "pending" and .current_phase == "verify")]' \
  ops/queue/queue.json)
N=$(echo "$WORKLIST" | jq 'length')

echo "## Verify"
echo "**Batch:** $BATCH_ID"
echo "**Work-list:** $N entries"
echo ""

emit_machine() {
  # Args: link_status orphans_status broken_json orphans_json per_note_json
  jq -n \
    --arg batch "$BATCH_ID" \
    --argjson worklist "$N" \
    --arg link_status "$1" \
    --arg orphan_status "$2" \
    --argjson links_scanned "${3:-0}" \
    --argjson broken "${4:-[]}" \
    --argjson orphans "${5:-[]}" \
    --argjson per_note "${6:-[]}" \
    '{
      batch: $batch,
      worklist: $worklist,
      link_health: {status:$link_status, scanned:$links_scanned, broken:$broken},
      orphan_check: {status:$orphan_status, count:($orphans | length), ids:$orphans},
      per_note: $per_note
    }'
}

if [ "$N" -eq 0 ]; then
  echo "### Vault-scope checks"
  echo "- Link health: SKIP (no work-list)"
  echo "- Orphan check: SKIP (no work-list)"
  echo ""
  echo "### Per-note structural results"
  echo "- (none)"
  echo ""
  echo "### Machine output"
  emit_machine SKIP SKIP 0 '[]' '[]' '[]'
  exit 0
fi

# ── Vault-scope link health ────────────────────────────────────
broken=0
links_scanned=0
broken_details=""
broken_jsonl=""
while IFS= read -r entry; do
  path=$(echo "$entry" | jq -r '.target_path')
  id=$(echo "$entry" | jq -r '.id')
  [ -f "$path" ] || continue
  while IFS= read -r link; do
    [ -n "$link" ] || continue
    links_scanned=$((links_scanned + 1))
    target=$(echo "$link" | sed -E 's/.*\[\[([^]]+)\]\].*/\1/')
    if [ -z "$(find . -name "${target}.md" -not -path "./.git/*" -print -quit 2>/dev/null)" ]; then
      broken=$((broken + 1))
      broken_details="${broken_details}    - $id → [[${target}]]\n"
      broken_jsonl="${broken_jsonl}$(jq -nc --arg id "$id" --arg target "$target" '{id:$id, target:$target}')"$'\n'
    fi
  done < <(grep -oE '\[\[[^]]+\]\]' "$path" 2>/dev/null)
done < <(echo "$WORKLIST" | jq -c '.[]')

if [ "$broken" -eq 0 ]; then
  link_status="PASS"
else
  link_status="FAIL"
fi

broken_json=$(printf '%s' "$broken_jsonl" | jq -s -c '.')

echo "### Vault-scope checks"
echo "- Link health: $link_status ($links_scanned links scanned, $broken broken)"
[ -n "$broken_details" ] && printf "%b" "$broken_details"

# ── Vault-scope orphan check ───────────────────────────────────
# Build the set of every wiki-link target that lives inside any topic map.
# A note is non-orphaned iff its filename (basename without .md) is in that
# set — filenames === titles verbatim, so the comparison is direct.
moc_link_targets=$(collect_moc_link_targets)

orphans=0
orphan_details=""
orphans_jsonl=""
while IFS= read -r entry; do
  path=$(echo "$entry" | jq -r '.target_path')
  id=$(echo "$entry" | jq -r '.id')
  [ -f "$path" ] || continue
  bn=$(basename "$path" .md)
  if ! printf '%s\n' "$moc_link_targets" | grep -Fxq "$bn"; then
    orphans=$((orphans + 1))
    orphan_details="${orphan_details}    - $id (no topic-map mention)\n"
    orphans_jsonl="${orphans_jsonl}$(jq -nc --arg id "$id" --arg path "$path" '{id:$id, target_path:$path}')"$'\n'
  fi
done < <(echo "$WORKLIST" | jq -c '.[]')

if [ "$orphans" -eq 0 ]; then
  orphan_status="PASS"
else
  orphan_status="FAIL"
fi
echo "- Orphan check: $orphan_status ($orphans orphans found)"
[ -n "$orphan_details" ] && printf "%b" "$orphan_details"
echo ""

orphans_json=$(printf '%s' "$orphans_jsonl" | jq -s -c '.')

# ── Per-note structural checks ─────────────────────────────────
echo "### Per-note structural results"
per_note_jsonl=""
while IFS= read -r entry; do
  path=$(echo "$entry" | jq -r '.target_path')
  id=$(echo "$entry" | jq -r '.id')
  gran=$(echo "$entry" | jq -r '.granularity')

  issues=()
  if [ ! -f "$path" ]; then
    echo "- $id ($path) — Validate: FAIL (file not found); Review: TBD"
    per_note_jsonl="${per_note_jsonl}$(jq -nc --arg id "$id" --arg path "$path" --arg gran "$gran" \
      '{id:$id, path:$path, granularity:$gran, validate:"FAIL", issues:["file not found"], review:"TBD"}')"$'\n'
    continue
  fi

  # Frontmatter delimiters
  if ! head -1 "$path" | grep -q '^---$'; then
    issues+=("missing opening ---")
  fi
  # Closing --- must exist after first
  if [ "$(grep -c '^---$' "$path")" -lt 2 ]; then
    issues+=("missing closing ---")
  fi
  # Description trailing period (warn-level)
  desc_line=$(grep '^description:' "$path" | head -1)
  if echo "$desc_line" | grep -qE '\.$'; then
    issues+=("trailing period on description")
  fi
  # Topics footer presence
  if ! grep -qE '^Topics:' "$path"; then
    issues+=("missing Topics footer")
  fi
  # Capture granularity: verbatim integrity (fenced block present, links only in footer)
  if [ "$gran" = "capture" ]; then
    if ! grep -q '^```' "$path"; then
      issues+=("missing fenced verbatim block")
    fi
  fi

  if [ "${#issues[@]}" -eq 0 ]; then
    verdict="PASS"
    detail=""
    issues_json='[]'
  else
    if [ "${#issues[@]}" -eq 1 ] && [[ "${issues[0]}" == "trailing period"* ]]; then
      verdict="WARN"
    else
      verdict="FAIL"
    fi
    detail=" ($(IFS=, ; echo "${issues[*]}"))"
    issues_json=$(printf '%s\n' "${issues[@]}" | jq -R -s -c 'split("\n") | map(select(. != ""))')
  fi

  echo "- $id ($path) — Validate: ${verdict}${detail}; Review: TBD"
  per_note_jsonl="${per_note_jsonl}$(jq -nc --arg id "$id" --arg path "$path" --arg gran "$gran" --arg verdict "$verdict" --argjson issues "$issues_json" \
    '{id:$id, path:$path, granularity:$gran, validate:$verdict, issues:$issues, review:"TBD"}')"$'\n'
done < <(echo "$WORKLIST" | jq -c '.[]')
echo ""

per_note_json=$(printf '%s' "$per_note_jsonl" | jq -s -c '.')

# ── Machine output ─────────────────────────────────────────────
echo "### Machine output"
emit_machine "$link_status" "$orphan_status" "$links_scanned" "$broken_json" "$orphans_json" "$per_note_json"
