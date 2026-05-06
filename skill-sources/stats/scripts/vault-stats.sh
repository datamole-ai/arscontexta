#!/bin/bash
# Ars Contexta — Vault Stats
# Emits the full --=={ stats }==-- block with vocabulary resolved,
# followed by a `# facts:` line for SKILL.md-driven interpretation.
set -e

# ── Vocabulary loader (duplicated per script, by design) ────────
NOTES_DIR="notes"
INBOX_DIR="inbox"
NOTE_PLURAL="notes"
TOPIC_MAP_PLURAL="mocs"
NOTE_TERM="note"
TOPIC_MAP_TERM="moc"

if [ -f ops/derivation-manifest.md ]; then
  while IFS='|' read -r _ universal domain _; do
    universal=$(echo "$universal" | xargs)
    domain=$(echo "$domain" | xargs)
    case "$universal" in
      notes)        NOTES_DIR="$domain"; NOTE_PLURAL="$domain" ;;
      inbox)        INBOX_DIR="$domain" ;;
      note)         NOTE_TERM="$domain" ;;
      topic_map)    TOPIC_MAP_TERM="$domain" ;;
      topic_maps)   TOPIC_MAP_PLURAL="$domain" ;;
    esac
  done < <(grep -E '^\| (notes|inbox|note|topic_map|topic_maps) ' ops/derivation-manifest.md 2>/dev/null || true)
fi

# ── Knowledge Graph ─────────────────────────────────────────────
TOTAL_FILES=$(find "$NOTES_DIR" -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
MOC_COUNT=$(find "$NOTES_DIR" -name "*.md" -type f -exec grep -l '^content_type: moc' {} + 2>/dev/null | wc -l | tr -d ' ')
NOTE_COUNT=$((TOTAL_FILES - MOC_COUNT))
LINK_COUNT=$(find "$NOTES_DIR" -name "*.md" -type f -exec grep -ohE '\[\[[^]]+\]\]' {} + 2>/dev/null | wc -l | tr -d ' ')

if [ "$NOTE_COUNT" -gt 0 ]; then
  AVG_LINKS=$(awk "BEGIN { printf \"%.1f\", $LINK_COUNT / $NOTE_COUNT }")
else
  AVG_LINKS="0.0"
fi
if [ "$NOTE_COUNT" -gt 1 ]; then
  POSSIBLE=$((NOTE_COUNT * (NOTE_COUNT - 1)))
  DENSITY=$(awk "BEGIN { printf \"%.4f\", $LINK_COUNT / $POSSIBLE }")
else
  DENSITY="N/A"
fi

# MOC coverage: count of non-MOC notes referenced from any MOC
COVERED=0
while IFS= read -r f; do
  [ -f "$f" ] || continue
  grep -q '^content_type: moc' "$f" 2>/dev/null && continue
  bn=$(basename "$f" .md)
  if find "$NOTES_DIR" -name "*.md" -type f -exec grep -l '^content_type: moc' {} + 2>/dev/null \
       | xargs grep -l "\[\[$bn\]\]" >/dev/null 2>&1; then
    COVERED=$((COVERED + 1))
  fi
done < <(find "$NOTES_DIR" -name "*.md" -type f 2>/dev/null)
if [ "$NOTE_COUNT" -gt 0 ]; then
  COVERAGE=$((COVERED * 100 / NOTE_COUNT))
else
  COVERAGE="0"
fi

# ── Health ──────────────────────────────────────────────────────
ORPHAN_COUNT=0
while IFS= read -r f; do
  [ -f "$f" ] || continue
  grep -q '^content_type: moc' "$f" 2>/dev/null && continue
  bn=$(basename "$f" .md)
  in=$(grep -rl "\[\[$bn\]\]" "$NOTES_DIR" 2>/dev/null | grep -v "^$f$" | wc -l | tr -d ' ')
  [ "$in" -eq 0 ] && ORPHAN_COUNT=$((ORPHAN_COUNT + 1))
done < <(find "$NOTES_DIR" -name "*.md" -type f 2>/dev/null)

DANGLING_COUNT=$(find "$NOTES_DIR" -name "*.md" -type f -exec grep -ohE '\[\[[^]]+\]\]' {} + 2>/dev/null \
  | sort -u \
  | while read -r link; do
      target=$(echo "$link" | sed 's/^\[\[//;s/\]\]$//')
      [ -z "$(find . -name "${target}.md" -not -path "./.git/*" -print -quit 2>/dev/null)" ] && echo "$target"
    done | wc -l | tr -d ' ')

MISSING_DESC=$(find "$NOTES_DIR" -name "*.md" -type f -exec grep -L '^description:' {} + 2>/dev/null | wc -l | tr -d ' ')
if [ "$TOTAL_FILES" -gt 0 ]; then
  COMPLIANCE=$(( (TOTAL_FILES - MISSING_DESC) * 100 / TOTAL_FILES ))
else
  COMPLIANCE=100
fi

# ── Pipeline ────────────────────────────────────────────────────
INBOX_COUNT=$(find "$INBOX_DIR" -maxdepth 1 -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
QUEUE_PENDING=0
QUEUE_DONE=0
if [ -f ops/queue/queue.json ]; then
  QUEUE_PENDING=$(jq '[.tasks[] | select(.status=="pending")] | length' ops/queue/queue.json 2>/dev/null || echo 0)
  QUEUE_DONE=$(jq '[.tasks[] | select(.status=="done")] | length' ops/queue/queue.json 2>/dev/null || echo 0)
fi
TOTAL_CONTENT=$((NOTE_COUNT + INBOX_COUNT))
if [ "$TOTAL_CONTENT" -gt 0 ]; then
  PROCESSED_PCT=$((NOTE_COUNT * 100 / TOTAL_CONTENT))
else
  PROCESSED_PCT=0
fi

# ── Growth ──────────────────────────────────────────────────────
WEEK_AGO=$(date -v-7d +%Y-%m-%d 2>/dev/null || date -d '7 days ago' +%Y-%m-%d 2>/dev/null)
THIS_WEEK_NOTES=0
THIS_WEEK_LINKS=0
if [ -n "$WEEK_AGO" ]; then
  while IFS= read -r f; do
    [ -f "$f" ] || continue
    created=$(grep '^created_at:' "$f" 2>/dev/null | head -1 | awk '{print $2}')
    [ -z "$created" ] && continue
    if [ "$created" \> "$WEEK_AGO" ] || [ "$created" = "$WEEK_AGO" ]; then
      THIS_WEEK_NOTES=$((THIS_WEEK_NOTES + 1))
      links=$(grep -ohE '\[\[[^]]+\]\]' "$f" 2>/dev/null | wc -l | tr -d ' ')
      THIS_WEEK_LINKS=$((THIS_WEEK_LINKS + links))
    fi
  done < <(find "$NOTES_DIR" -name "*.md" -type f 2>/dev/null)
fi

# ── System ──────────────────────────────────────────────────────
if [ -d self ]; then
  SELF_FILES=$(find self -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  SELF_STATUS="${SELF_FILES} files"
else
  SELF_STATUS="MISSING (invariant primitive)"
fi
OBS_PENDING=0
TENSION_PENDING=0
while IFS= read -r f; do
  [ -f "$f" ] || continue
  if grep -q '^content_type: observation' "$f" 2>/dev/null && grep -q '^status: pending' "$f" 2>/dev/null; then
    OBS_PENDING=$((OBS_PENDING + 1))
  fi
  if grep -q '^content_type: tension' "$f" 2>/dev/null && grep -qE '^status: (open|pending)' "$f" 2>/dev/null; then
    TENSION_PENDING=$((TENSION_PENDING + 1))
  fi
done < <(find "$NOTES_DIR" -name "*.md" -type f 2>/dev/null)

# ── Progress bar ────────────────────────────────────────────────
filled=$((PROCESSED_PCT / 5))
[ "$filled" -gt 20 ] && filled=20
empty=$((20 - filled))
bar="["
i=0
while [ "$i" -lt "$filled" ]; do bar="${bar}="; i=$((i + 1)); done
i=0
while [ "$i" -lt "$empty" ]; do bar="${bar} "; i=$((i + 1)); done
bar="${bar}]"

# Title-case helper (bash 3.2 compatible — no ${VAR^} which is bash 4+)
title_case() {
  local s="$1"
  printf '%s%s' "$(printf '%s' "${s:0:1}" | tr '[:lower:]' '[:upper:]')" "${s:1}"
}
NOTE_PLURAL_TC=$(title_case "$NOTE_PLURAL")
TOPIC_MAP_PLURAL_TC=$(title_case "$TOPIC_MAP_PLURAL")

# ── Output block ────────────────────────────────────────────────
cat <<EOF
--=={ stats }==--

  Knowledge Graph
  ===============
  ${NOTE_PLURAL_TC}:    ${NOTE_COUNT}
  Connections:        ${LINK_COUNT} (avg ${AVG_LINKS} per ${NOTE_TERM})
  ${TOPIC_MAP_PLURAL_TC}:    ${MOC_COUNT} (covering ${COVERAGE}% of ${NOTE_PLURAL})

  Health
  ======
  Orphans:      ${ORPHAN_COUNT}
  Dangling:     ${DANGLING_COUNT}
  Schema:       ${COMPLIANCE}% compliant

  Pipeline
  ========
  Processed:    ${bar} ${PROCESSED_PCT}%
  Inbox:        ${INBOX_COUNT} items
  Queue:        ${QUEUE_PENDING} pending tasks

  Growth
  ======
  This week:    +${THIS_WEEK_NOTES} ${NOTE_PLURAL}, +${THIS_WEEK_LINKS} connections
  Graph density: ${DENSITY}

  System
  ======
  Self space:      ${SELF_STATUS}
  Observations:    ${OBS_PENDING} pending
  Tensions:        ${TENSION_PENDING} open

  Generated by Ars Contexta
EOF
echo ""
echo "# facts: COMPLIANCE=${COMPLIANCE} OBS_PENDING=${OBS_PENDING} TENSION_PENDING=${TENSION_PENDING} PROCESSED_PCT=${PROCESSED_PCT} THIS_WEEK_NOTES=${THIS_WEEK_NOTES}"
