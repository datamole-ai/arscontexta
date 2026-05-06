#!/bin/bash
# Ars Contexta — Health Check
# Runs structural diagnostics across 7 categories. Cat 4 (description quality)
# is LLM-judgment and stays in SKILL.md.
#
# Output: per-category blocks (numeric order, with PENDING marker for Cat 4)
#         plus scan summary and maintenance signals.
# Exit:   0 always when run completes; nonzero only on tool/vault errors.
set -e

# ── Vocabulary loader ──────────────────────────────────────────
NOTES_DIR="notes"
INBOX_DIR="inbox"
ARCHIVE_DIR="archive"
NOTE_TERM="note"
TOPIC_MAP_TERM="moc"
TOPIC_MAP_PLURAL="mocs"

if [ -f ops/derivation-manifest.md ]; then
  while IFS='|' read -r _ universal domain _; do
    universal=$(echo "$universal" | xargs)
    domain=$(echo "$domain" | xargs)
    case "$universal" in
      notes)        NOTES_DIR="$domain" ;;
      inbox)        INBOX_DIR="$domain" ;;
      archive)      ARCHIVE_DIR="$domain" ;;
      note)         NOTE_TERM="$domain" ;;
      topic_map)    TOPIC_MAP_TERM="$domain" ;;
      topic_maps)   TOPIC_MAP_PLURAL="$domain" ;;
    esac
  done < <(grep -E '^\| (notes|inbox|archive|note|topic_map|topic_maps) ' ops/derivation-manifest.md 2>/dev/null || true)
fi

# ── Helpers ────────────────────────────────────────────────────
note_files() {
  find "$NOTES_DIR" -name "*.md" -type f 2>/dev/null
}

# Print a per-category header line.
emit_header() {
  printf '[%s] %-30s %s\n' "$1" "$2" "$3"
}

# ── Scan summary ────────────────────────────────────────────────
TOTAL_NOTES=$(note_files | wc -l | tr -d ' ')
MOC_COUNT=$(note_files | xargs grep -l '^content_type: moc' 2>/dev/null | wc -l | tr -d ' ')
INBOX_COUNT=$(find "$INBOX_DIR" -maxdepth 1 -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
echo "# scan: notes=$TOTAL_NOTES mocs=$MOC_COUNT inbox=$INBOX_COUNT"
echo ""

# ── Category 1: Schema Compliance ───────────────────────────────
cat1_status="PASS"
cat1_details=""
while IFS= read -r f; do
  [ -f "$f" ] || continue
  if ! head -1 "$f" | grep -q '^---$'; then
    cat1_status="FAIL"
    cat1_details="${cat1_details}      - $f — no YAML frontmatter\n"
    continue
  fi
  if ! grep -q '^description:' "$f"; then
    [ "$cat1_status" = "PASS" ] && cat1_status="WARN"
    cat1_details="${cat1_details}      - $f — missing description field\n"
  fi
done < <(note_files)
emit_header 1 "Schema Compliance" "$cat1_status"
[ -n "$cat1_details" ] && printf "%b" "$cat1_details"
echo ""

# ── Category 2: Orphan Detection ────────────────────────────────
cat2_status="PASS"
cat2_details=""
now_epoch=$(date +%s)
while IFS= read -r f; do
  [ -f "$f" ] || continue
  bn=$(basename "$f" .md)
  # Skip MOCs from orphan check
  grep -q '^content_type: moc' "$f" 2>/dev/null && continue
  incoming=$(grep -rl "\[\[$bn\]\]" "$NOTES_DIR" 2>/dev/null | grep -v "^$f$" | wc -l | tr -d ' ')
  [ "$incoming" -gt 0 ] && continue
  mtime=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null)
  age_days=$(( (now_epoch - mtime) / 86400 ))
  if [ "$age_days" -lt 1 ]; then
    tier="INFO"
  elif [ "$age_days" -le 7 ]; then
    tier="WARN"
    [ "$cat2_status" = "PASS" ] && cat2_status="WARN"
  else
    tier="FAIL"
    cat2_status="FAIL"
  fi
  cat2_details="${cat2_details}      - $f (${age_days}d, 0 incoming) [$tier]\n"
done < <(note_files)
emit_header 2 "Orphan Detection" "$cat2_status"
[ -n "$cat2_details" ] && printf "%b" "$cat2_details"
echo ""

# ── Category 3: Link Health ─────────────────────────────────────
# `sort -u` upstream already dedupes link targets, so no associative array needed.
# Avoiding `declare -A` keeps this bash 3.2 compatible (macOS default).
cat3_status="PASS"
cat3_details=""
while IFS= read -r line; do
  target=$(echo "$line" | sed -E 's/.*\[\[([^]]+)\]\].*/\1/')
  [ -n "$target" ] || continue
  if [ -z "$(find . -name "${target}.md" -not -path "./.git/*" -print -quit 2>/dev/null)" ]; then
    cat3_status="FAIL"
    refs=$(grep -rl "\[\[$target\]\]" --include='*.md' . 2>/dev/null | grep -v '/.git/' | head -3 | sed 's/^/        /')
    cat3_details="${cat3_details}      - [[$target]] referenced in:\n$refs\n"
  fi
done < <(grep -rohE '\[\[[^]]+\]\]' --include='*.md' . 2>/dev/null | grep -v '/.git/' | sort -u)
emit_header 3 "Link Health" "$cat3_status"
[ -n "$cat3_details" ] && printf "%b" "$cat3_details"
echo ""

# ── Category 4: Description Quality (LLM judgment) ──────────────
emit_header 4 "Description Quality" "PENDING (LLM judgment)"
echo ""

# ── Category 5: Three-Space Boundaries ──────────────────────────
cat5_status="PASS"
cat5_details=""

# 5a: ops-pattern fields in notes
hits_5a=$(grep -rlE '^(current_phase|completed_phases|batch|queue_id):' "$NOTES_DIR" --include='*.md' 2>/dev/null || true)
if [ -n "$hits_5a" ]; then
  cat5_status="WARN"
  while IFS= read -r f; do
    [ -n "$f" ] && cat5_details="${cat5_details}      - $f — ops-pattern field in note (5a)\n"
  done <<< "$hits_5a"
fi

# 5b: agent-reflection patterns in notes
hits_5b=$(grep -rilE '(my methodology|i observed that|agent reflection|session learning|i learned)' "$NOTES_DIR" --include='*.md' 2>/dev/null || true)
if [ -n "$hits_5b" ]; then
  cat5_status="WARN"
  while IFS= read -r f; do
    [ -n "$f" ] && cat5_details="${cat5_details}      - $f — agent-reflection pattern in note (5b)\n"
  done <<< "$hits_5b"
fi

# 5d: temporal/queue content in self/
if [ -d self ]; then
  hits_5d=$(grep -rlE '^(current_phase|status|queue):' self --include='*.md' 2>/dev/null || true)
  if [ -n "$hits_5d" ]; then
    cat5_status="WARN"
    while IFS= read -r f; do
      [ -n "$f" ] && cat5_details="${cat5_details}      - $f — temporal/queue in self/ (5d)\n"
    done <<< "$hits_5d"
  fi
fi

# 5f: self/ presence
if [ ! -d self ]; then
  cat5_status="FAIL"
  cat5_details="${cat5_details}      - self/ directory missing — invariant primitive (5f)\n"
elif [ ! -f self/identity.md ] || [ ! -f self/methodology.md ] || [ ! -f self/goals.md ]; then
  cat5_status="FAIL"
  cat5_details="${cat5_details}      - self/ exists but missing required files (identity/methodology/goals) (5f)\n"
fi

emit_header 5 "Three-Space Boundaries" "$cat5_status"
[ -n "$cat5_details" ] && printf "%b" "$cat5_details"
echo ""

# ── Category 6: Processing Throughput ───────────────────────────
queue_count=$(find ops/queue -maxdepth 1 -name '*.md' -type f 2>/dev/null | wc -l | tr -d ' ')
total_content=$((INBOX_COUNT + TOTAL_NOTES))
if [ "$total_content" -gt 0 ]; then
  ratio=$((INBOX_COUNT * 100 / total_content))
else
  ratio=0
fi
cat6_status="PASS"
if [ "$ratio" -gt 75 ]; then
  cat6_status="FAIL"
elif [ "$ratio" -gt 50 ] || [ "$INBOX_COUNT" -gt 20 ]; then
  cat6_status="WARN"
fi
emit_header 6 "Processing Throughput" "$cat6_status"
echo "      inbox: $INBOX_COUNT | $NOTES_DIR: $TOTAL_NOTES | in-progress: $queue_count | ratio: ${ratio}%"
echo ""

# ── Category 7: Stale Notes ─────────────────────────────────────
cat7_status="PASS"
cat7_details=""
while IFS= read -r f; do
  [ -f "$f" ] || continue
  bn=$(basename "$f" .md)
  grep -q '^content_type: moc' "$f" 2>/dev/null && continue
  mtime=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null)
  age=$(( (now_epoch - mtime) / 86400 ))
  [ "$age" -le 30 ] && continue
  incoming=$(grep -rl "\[\[$bn\]\]" "$NOTES_DIR" 2>/dev/null | grep -v "^$f$" | wc -l | tr -d ' ')
  [ "$incoming" -ge 2 ] && continue
  if [ "$age" -gt 90 ] && [ "$incoming" -eq 0 ]; then
    tier="FAIL"
    cat7_status="FAIL"
  else
    tier="WARN"
    [ "$cat7_status" = "PASS" ] && cat7_status="WARN"
  fi
  cat7_details="${cat7_details}      - $f (${age}d, ${incoming} incoming) [$tier]\n"
done < <(note_files)
emit_header 7 "Stale Notes" "$cat7_status"
[ -n "$cat7_details" ] && printf "%b" "$cat7_details"
echo ""

# ── Category 8: MOC Coherence ───────────────────────────────────
cat8_status="PASS"
cat8_details=""
while IFS= read -r moc; do
  [ -f "$moc" ] || continue
  grep -q '^content_type: moc' "$moc" 2>/dev/null || continue
  moc_bn=$(basename "$moc" .md)
  linked=$(grep -rl "\[\[$moc_bn\]\]" "$NOTES_DIR" --include='*.md' 2>/dev/null | grep -v "^$moc$" | wc -l | tr -d ' ')
  if [ "$linked" -lt 5 ]; then
    [ "$cat8_status" = "PASS" ] && cat8_status="WARN"
    cat8_details="${cat8_details}      - $moc_bn: $linked notes [WARN — underdeveloped]\n"
  elif [ "$linked" -gt 50 ]; then
    [ "$cat8_status" = "PASS" ] && cat8_status="WARN"
    cat8_details="${cat8_details}      - $moc_bn: $linked notes [WARN — oversized]\n"
  elif [ "$linked" -gt 40 ]; then
    cat8_details="${cat8_details}      - $moc_bn: $linked notes [INFO — approaching threshold]\n"
  else
    cat8_details="${cat8_details}      - $moc_bn: $linked notes [PASS]\n"
  fi
  # bare-link check (links without ` — ` context phrase)
  bare=$(grep -E '^\s*- \[\[' "$moc" 2>/dev/null | grep -v ' — ' | wc -l | tr -d ' ')
  if [ "$bare" -gt 0 ]; then
    [ "$cat8_status" = "PASS" ] && cat8_status="WARN"
    cat8_details="${cat8_details}        $bare bare links without context phrases\n"
  fi
done < <(note_files)
emit_header 8 "MOC Coherence" "$cat8_status"
[ -n "$cat8_details" ] && printf "%b" "$cat8_details"
echo ""

# ── Maintenance Signals ─────────────────────────────────────────
echo "Maintenance Signals:"
if [ "$INBOX_COUNT" -ge 3 ]; then
  echo "    - inbox: $INBOX_COUNT items (threshold: 3) [TRIGGERED]"
else
  echo "    - inbox: $INBOX_COUNT items (threshold: 3) [OK]"
fi
pending=$(jq '[.tasks[] | select(.status=="pending")] | length' ops/queue/queue.json 2>/dev/null || echo 0)
if [ "$pending" -ge 1 ]; then
  echo "    - queue: $pending pending tasks [TRIGGERED]"
else
  echo "    - queue: 0 pending tasks [OK]"
fi
echo ""
echo "# done"
