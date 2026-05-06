#!/bin/bash
# Ars Contexta — Verify (batch phase)
# Args: BATCH_ID
# Output: ## Verify block (vault-scope checks + per-note structural results,
#         each per-note line ends with "Review: TBD" for the LLM to fill in)
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

if [ "$N" -eq 0 ]; then
  echo "### Vault-scope checks"
  echo "- Link health: SKIP (no work-list)"
  echo "- Orphan check: SKIP (no work-list)"
  echo ""
  echo "### Per-note structural results"
  echo "- (none)"
  echo ""
  exit 0
fi

# ── Vault-scope link health ────────────────────────────────────
broken=0
links_scanned=0
broken_details=""
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
    fi
  done < <(grep -oE '\[\[[^]]+\]\]' "$path" 2>/dev/null)
done < <(echo "$WORKLIST" | jq -c '.[]')

if [ "$broken" -eq 0 ]; then
  link_status="PASS"
else
  link_status="FAIL"
fi

echo "### Vault-scope checks"
echo "- Link health: $link_status ($links_scanned links scanned, $broken broken)"
[ -n "$broken_details" ] && printf "%b" "$broken_details"

# ── Vault-scope orphan check ───────────────────────────────────
orphans=0
orphan_details=""
while IFS= read -r entry; do
  path=$(echo "$entry" | jq -r '.target_path')
  id=$(echo "$entry" | jq -r '.id')
  [ -f "$path" ] || continue
  bn=$(basename "$path" .md)
  # Note must appear in a MOC's body
  in_moc=$(find "$NOTES_DIR" -name "*.md" -exec grep -l '^content_type: moc' {} + 2>/dev/null \
    | xargs grep -l "\[\[$bn\]\]" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$in_moc" -eq 0 ]; then
    orphans=$((orphans + 1))
    orphan_details="${orphan_details}    - $id (no topic-map mention)\n"
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

# ── Per-note structural checks ─────────────────────────────────
echo "### Per-note structural results"
while IFS= read -r entry; do
  path=$(echo "$entry" | jq -r '.target_path')
  id=$(echo "$entry" | jq -r '.id')
  gran=$(echo "$entry" | jq -r '.granularity')

  issues=()
  if [ ! -f "$path" ]; then
    echo "- $id ($path) — Validate: FAIL (file not found); Review: TBD"
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
  else
    # If only the trailing-period issue, WARN; else FAIL
    if [ "${#issues[@]}" -eq 1 ] && [[ "${issues[0]}" == "trailing period"* ]]; then
      verdict="WARN"
    else
      verdict="FAIL"
    fi
    detail=" ($(IFS=, ; echo "${issues[*]}"))"
  fi

  echo "- $id ($path) — Validate: ${verdict}${detail}; Review: TBD"
done < <(echo "$WORKLIST" | jq -c '.[]')
echo ""
